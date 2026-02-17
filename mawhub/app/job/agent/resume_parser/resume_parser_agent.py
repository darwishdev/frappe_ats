
from typing import Dict, Iterator,  Literal, Type, TypedDict, cast,  Optional, Union
from mawhub.app.job.agent.resume_parser.instructions import CUNKER_SYSTEM_INSTRUCTION, EXTRACTOR_SYSTEM_INSTRUCTION
from concurrent.futures import ThreadPoolExecutor, as_completed
from google import genai
from google.genai import types
from mawhub.pkg.objectutils.objectutils import to_typed_dict
from mawhub.app.job.agent.resume_parser.types import AgentSectionDict, ChunkedResumeModel, EducationListModel, ExperienceListModel, PersonalInfoModel, ProjectListModel, SectionNames, SkillListModel, SummaryModel
from mawhub.app.job.dto.applicant_resume_dto import ApplicantResumeDTO


class AgentSectionEvent(TypedDict):
    name: SectionNames
    content: AgentSectionDict


class ResumeParserChunkedEvent(TypedDict):
    event: Literal["chuncked"]
    data: dict[SectionNames,str]
class ResumeParserUpdateEvent(TypedDict):
    event: Literal["update"]
    data: AgentSectionEvent


class ResumeParserFinalEvent(TypedDict):
    event: Literal["final"]
    data: ApplicantResumeDTO

class ResumeParserErrorEvent(TypedDict):
    event: Literal["error"]
    data: str

ResumeParserEvent = Union[
    ResumeParserChunkedEvent,
    ResumeParserUpdateEvent,
    ResumeParserErrorEvent,
    ResumeParserFinalEvent
]

# --- 4. Workflow Logic ---

class ResumeWorkflow:
    def __init__(
        self,
        client: genai.Client,
        model_name: str
    ):
        self.client = client
        self.default_model = model_name

    def agent_meta_labeler(self, raw_text: str, model_id: str) -> tuple[ChunkedResumeModel,ResumeParserChunkedEvent]:
        prompt = f"Analyze this resume text and split it into sections: 'personal', 'summary', 'skills', 'experience', 'projects', 'education'.\n\nText:\n{raw_text}"
        response = self.client.models.generate_content(
            model=model_id,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=CUNKER_SYSTEM_INSTRUCTION,
                temperature=0.0,
                top_p=0.1,
                max_output_tokens=6000,
                response_mime_type="application/json",
                response_schema=ChunkedResumeModel
            )
        )
        resp = cast(ChunkedResumeModel, response.parsed)
        event_data : dict[SectionNames,str]= {}
        for value in resp.sections:
            event_data[value.name] = value.content
        return resp,{"event" : "chuncked" , "data" : event_data}
    def extraction_worker(self, section_name: str, text_chunk: str, schema: Type,
                          model_id: str) -> AgentSectionDict | str:
        prompt = f"Extract the {section_name} from the following text.\n\nText:\n{text_chunk}"
        config_args = {
            "model": model_id,
            "contents": prompt,
            "config": types.GenerateContentConfig(
                system_instruction=EXTRACTOR_SYSTEM_INSTRUCTION,
                response_mime_type="application/json",
                response_schema=schema,
                temperature=0.0,
                top_p=0.1,
            )
        }

        response = self.client.models.generate_content(**config_args)
        parsed = response.parsed
        if hasattr(parsed, 'items'):
            parsed_items = getattr(parsed, "items")
            parsed_items_dict = to_typed_dict(parsed_items, AgentSectionDict)
            return cast(AgentSectionDict, parsed_items_dict)
        resp = to_typed_dict(parsed, AgentSectionDict)
        return cast(AgentSectionDict, resp)

    def final_to_dto(self,final_event: dict[SectionNames,AgentSectionDict] )->ApplicantResumeDTO:
        personl = cast(dict ,final_event["personal"])
        summary = cast(dict ,final_event["summary"])
        return {
            "resume_hash" : "",
            "applicant_name" : personl.get("name") or "",
            "email" : personl.get("email") or "",
            "location" : personl.get("location") or "",
            "phone" : personl.get("phone") or "",
            "summary" : summary["summary"],
            "file_path" : "",
                }
    def run(
            self,
            resume_text: str,
            model_overrides: Optional[Dict[str, str]] = None
    ) -> Iterator[ResumeParserEvent]:
        """
        model_overrides: Dict where key is step_id ('labeler', 'experience', etc.)
                         and value is the model name.
        """
        overrides = model_overrides or {}

        # Helper to get model for a specific step
        def get_model(step_id: str) -> str:
            return overrides.get(step_id, self.default_model)

        labeler_model = get_model("labeler")
        chunked_data , chunked_event = self.agent_meta_labeler(resume_text, labeler_model)
        yield chunked_event

        mapping = {
            "personal": PersonalInfoModel,
            "skills": SkillListModel,
            "experience": ExperienceListModel,
            "summary": SummaryModel,
            "projects": ProjectListModel,
            "education": EducationListModel
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

            final_response : dict[SectionNames,AgentSectionDict] = {}
            for future in as_completed(future_to_section):
                section_name = future_to_section[future]
                try:
                    section_data = future.result()
                    res_section: AgentSectionEvent = {
                        "name": section_name,
                        "content": section_data,
                    }
                    yield {
                        "event": "update",
                        "data": res_section
                    }
                    final_response[section_name] = section_data
                except Exception as e:
                    yield {"event": "error", "data": str(e)}
            final_event_dto = self.final_to_dto(final_response)
            yield {
                "event": "final",
                "data": final_event_dto
            }

