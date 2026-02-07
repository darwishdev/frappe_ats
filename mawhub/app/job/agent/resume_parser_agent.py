from typing import Dict,  Iterator, List, Literal, Type, TypedDict, cast, Callable, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from frappe import Union
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

class ApplicantExperience(BaseModel):
    company: str = Field(
        description="Company or organization name exactly as written in the resume. Do not normalize."
    )
    role: str = Field(
        description="Job title or role exactly as written. Do not merge multiple roles."
    )
    from_date: str = Field(
        description="Start date exactly as written (no normalization or inference)."
    )
    to_date: str = Field(
        description="End date exactly as written. If ongoing, return the literal text such as 'Present'."
    )
    description: str = Field(
        description="Responsibilities and achievements exactly as written. Preserve wording."
    )

class ApplicantEducation(BaseModel):
    institution: str = Field(
        description="Institution or university name exactly as written."
    )
    degree: str = Field(
        description="Degree or certification exactly as written. Do not infer level."
    )
    from_date: str = Field(
        description="Start date exactly as written."
    )
    to_date: str = Field(
        description="End or graduation date exactly as written."
    )

class ApplicantProject(BaseModel):
    title: str = Field(
        description="Project name exactly as written."
    )
    description: str = Field(
        description="Project description exactly as written. Do not summarize."
    )
    link: str = Field(
        description="Project URL if present. Otherwise return empty string."
    )

class ApplicantLink(BaseModel):
    label: str = Field(
        description="Link label such as GitHub, LinkedIn, Portfolio exactly as written."
    )
    url: str = Field(
        description="Full URL exactly as written."
    )

class ExperienceList(BaseModel):
    items: List[ApplicantExperience] = Field(
        description="List of distinct work experience roles. Do not merge roles."
    )

class ProjectList(BaseModel):
    items: List[ApplicantProject] = Field(
        description="List of projects. Each item must represent one project only."
    )

class EducationList(BaseModel):
    items: List[ApplicantEducation] = Field(
        description="List of education records. One record per degree or program."
    )

SectionNames = Literal["personal" , "summary" , "skills" , "experience" , "projects" , "education"]
class ResumeSection(BaseModel):
    name: SectionNames = Field(
        description="One of exactly: personal, summary, skills, experience, projects, education"
    )
    content: str = Field(
        description="Original resume text belonging to this section only. Do not rewrite."
    )

class ChunkedResume(BaseModel):
    sections: List[ResumeSection] = Field(
        description="Resume text split into the predefined section names only."
    )
class SkillList(BaseModel):
    items: List[str] = Field(description="A list of technical and soft skills extracted from the text")
# --- 2. Workflow Logic ---

class PersonalInfo(BaseModel):
    name: str = Field(description="Full candidate name as written in the resume")

    email: str = Field(
        description="Email address from the resume. Return empty string if not found"
    )

    phone: str = Field(
        description="Phone number as written. Return empty string if missing"
    )

    location: str = Field(
        description="City/country or location text from the resume"
    )

    links: List[str] = Field(
        description="List of profile or portfolio URLs (LinkedIn, GitHub, website). Empty list if none"
    )

AgentSection = Union[PersonalInfo ,str, SkillList,ExperienceList,ProjectList,EducationList]
class AgentSectionEvent(TypedDict):
    name: SectionNames
    content: AgentSection

class ResumeParserUpdateEvent(TypedDict):
    event: Literal["update"]
    data: AgentSectionEvent


class ResumeParserErrorEvent(TypedDict):
    event: Literal["error"]
    data: str


ResumeParserEvent = Union[
        ResumeParserUpdateEvent,
        ResumeParserErrorEvent
]


# ... (Wrapper Models: ExperienceList, ProjectList, EducationList, SkillList stay same)

class ResumeWorkflow:
    def __init__(
        self,
        client: genai.Client,
        model_name: str
    ):
        self.client = client
        self.default_model = model_name

    def agent_meta_labeler(self, raw_text: str, model_id: str) -> ChunkedResume:
        SYSTEM_INSTRUCTION = """
        You are a resume labeling engine.

        Your task is to analyze raw resume text and return a JSON object
        with the following sections only:
        - personal
        - summary
        - skills
        - experience
        - projects
        - education

        Definitions:
        - personal: name, job title, contact info, location, links only
        - summary: profile or professional summary
        - skills: technical skills, tools, technologies
        - experience: work experience and internships
        - projects: personal or professional projects
        - education: degrees, institutes, courses

        Rules:
        - Preserve original text exactly
        - Do not infer or rewrite content
        - Do not duplicate content across sections
        - If a section is missing, return it as an empty string
        """
        prompt = f"Analyze this resume text and split it into sections: 'personal', 'summary', 'skills', 'experience', 'projects', 'education'.\n\nText:\n{raw_text}"
        response = self.client.models.generate_content(
            model=model_id,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.0,
                top_p=0.1,
                max_output_tokens=6000,
                response_mime_type="application/json",
                response_schema=ChunkedResume
            )
        )
        return cast(ChunkedResume, response.parsed)

    def extraction_worker(self, section_name: str, text_chunk: str, schema: Type, model_id:str)->AgentSection:
        is_plain_text = (schema is str)
        GLOBAL_EXTRACTOR_INSTRUCTIONS = """
        You are a resume information extraction engine.

        Rules:
        - Extract ONLY from provided text
        - Do not infer missing values
        - Preserve original wording
        - Follow the schema field descriptions strictly
        - Return empty values if missing
        """
        prompt = f"Extract the {section_name} from the following text.\n\nText:\n{text_chunk}"

        config_args = {
            "model": model_id,
            "contents": prompt,
            "config": types.GenerateContentConfig(
                system_instruction=GLOBAL_EXTRACTOR_INSTRUCTIONS,
                response_mime_type="text/plain" if is_plain_text else "application/json",
                response_schema=None if is_plain_text else schema,
                temperature=0.0,
                top_p=0.1,
            )
        }

        response = self.client.models.generate_content(**config_args)
        return cast(AgentSection,response.parsed)


    def run(
            self,
            resume_text: str,
            model_overrides: Optional[Dict[str, str]] = None
        )->Iterator[ResumeParserEvent]:
        """
        model_overrides: Dict where key is step_id ('labeler', 'experience', etc.)
                         and value is the model name.
        """
        overrides = model_overrides or {}

        # Helper to get model for a specific step
        def get_model(step_id: str) -> str:
            return overrides.get(step_id, self.default_model)

        labeler_model = get_model("labeler")
        chunked_data = self.agent_meta_labeler(resume_text, labeler_model)

        mapping = {
            "personal": PersonalInfo,
            "skills": SkillList,
            "experience": ExperienceList,
            "summary" : str,
            "projects": ProjectList,
            "education": EducationList
        }

        tasks = []
        for section in chunked_data.sections:
            clean_name = section.name.lower().strip()
            schema = mapping.get(clean_name)
            if schema:
                # Get model specific to this section, or fallback to default
                section_model = get_model(clean_name)
                tasks.append((clean_name, section.content, schema, section_model))

        with ThreadPoolExecutor() as executor:
            future_to_section = {
                executor.submit(self.extraction_worker, name, text, schema, m_id): name
                for name, text, schema, m_id in tasks
            }

            for future in as_completed(future_to_section):
                section_name = future_to_section[future]
                try:
                    section_data = future.result()
                    res_section : AgentSectionEvent = {
                        "name" : section_name,
                        "content": section_data,
                    }
                    yield {
                        "event": "update",
                        "data": res_section
                    }
                except Exception as e:
                    yield {"event": "error", "data": str(e)}
