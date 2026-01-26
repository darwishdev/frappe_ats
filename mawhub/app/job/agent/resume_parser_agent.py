import json
from typing import Dict,  Iterator, List, Literal, Type, TypedDict, cast, Callable, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from frappe.utils import hashlib
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

# Import your DTOs
from mawhub.app.job.dto.applicant_resume import (
    ApplicantEducation, ApplicantExperience,
    ApplicantProject, ApplicantResumeDTO, PersonalInfo
)

# --- 1. Wrapper Models (REQUIRED for Gemini Lists) ---
# The SDK cannot handle List[Model] directly, so we wrap them.
class ExperienceList(BaseModel):
    items: List[ApplicantExperience]

class ProjectList(BaseModel):
    items: List[ApplicantProject]

class EducationList(BaseModel):
    items: List[ApplicantEducation]

class ResumeSection(BaseModel):
    name: str = Field(description="One of: 'personal', 'summary', 'skills', 'experience', 'projects', 'education'")
    content: str

class ChunkedResume(BaseModel):
    sections: List[ResumeSection]
class SkillList(BaseModel):
    items: List[str] = Field(description="A list of technical and soft skills extracted from the text")
# --- 2. Workflow Logic ---
class AgentSection(TypedDict):
    name: str
    content: str
class AgentEvent(TypedDict):
    event: Literal["update" , "final" , "error"]
    data: ApplicantResumeDTO | AgentSection | str


# ... (Wrapper Models: ExperienceList, ProjectList, EducationList, SkillList stay same)

class ResumeWorkflow:
    def __init__(
        self,
        client: genai.Client,
        model_name: str,
        get_cache_fn: Callable[[str, str], Optional[str]],
        set_cache_fn: Callable[[str, str, dict], None]
    ):
        self.client = client
        self.default_model = model_name
        self.get_cache_fn = get_cache_fn
        self.set_cache_fn = set_cache_fn

    def get_text_hash(self, text: str) -> str:
        clean_text = text.strip().encode('utf-8')
        return hashlib.sha256(clean_text).hexdigest()

    def agent_meta_labeler(self, raw_text: str, model_id: str) -> ChunkedResume:
        prompt = f"Analyze this resume text and split it into sections: 'personal', 'summary', 'skills', 'experience', 'projects', 'education'.\n\nText:\n{raw_text}"
        response = self.client.models.generate_content(
            model=model_id,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ChunkedResume
            )
        )
        return cast(ChunkedResume, response.parsed)

    def extraction_worker(self, section_name: str, text_chunk: str, schema: Type, model_id: str):
        is_plain_text = (schema is str)
        prompt = f"Extract the {section_name} from the following text.\n\nText:\n{text_chunk}"

        config_args = {
            "model": model_id,
            "contents": prompt,
            "config": types.GenerateContentConfig(
                response_mime_type="text/plain" if is_plain_text else "application/json",
                response_schema=schema if not is_plain_text else None
            )
        }

        response = self.client.models.generate_content(**config_args)

        if is_plain_text:
            return response.text.strip() if response.text else ""

        res = response.parsed
        items = None
        if res is not None:
            if hasattr(res, 'items'):
                items = getattr(res, 'items')
            elif isinstance(res, dict) and 'items' in res:
                items = res['items']

        if items is not None and isinstance(items, list):
            return [item.model_dump() if isinstance(item, BaseModel) else item for item in items]

        if isinstance(res, BaseModel):
            return res.model_dump()

        return res

    def run(self, resume_text: str, model_overrides: Optional[Dict[str, str]] = None) ->Iterator[AgentEvent]:
        """
        model_overrides: Dict where key is step_id ('labeler', 'experience', etc.)
                         and value is the model name.
        """
        overrides = model_overrides or {}

        # Helper to get model for a specific step
        def get_model(step_id: str) -> str:
            return overrides.get(step_id, self.default_model)

        text_hash = self.get_text_hash(resume_text)

        # Cache key includes the override dict string to ensure unique caches per configuration
        config_hash = hashlib.md5(json.dumps(overrides, sort_keys=True).encode()).hexdigest()

        # # 1. Check Cache
        if self.get_cache_fn:
            cached = self.get_cache_fn(f"{text_hash}_{config_hash}", self.default_model)
            if cached:
                final_res = json.loads(cached) if isinstance(cached, str) else cached
                yield {"event": "update", "data": final_res}
                return final_res

        # 2. Step 1: Labeling
        labeler_model = get_model("labeler")
        chunked_data = self.agent_meta_labeler(resume_text, labeler_model)
        mapping = {
            "personal": PersonalInfo,
            "summary": str,
            "skills": SkillList,
            "experience": ExperienceList,
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

        results = {}
        with ThreadPoolExecutor() as executor:
            future_to_section = {
                executor.submit(self.extraction_worker, name, text, schema, m_id): name
                for name, text, schema, m_id in tasks
            }

            for future in as_completed(future_to_section):
                section_name = future_to_section[future]
                try:
                    section_data = future.result()
                    if section_name == 'skills' and isinstance(section_data , list):
                        results[section_name] = ','.join(cast(list,section_data))
                    else:
                        results[section_name] = section_data
                    res_section : AgentSection = {
                        "name" : section_name,
                        "content": json.dumps(section_data),
                    }
                    yield {
                        "event": "update",
                        "data": res_section
                    }
                except Exception as e:
                    yield {"event": "error", "data": str(e)}

        # 4. Finalize
        if self.set_cache_fn:
            self.set_cache_fn(f"{text_hash}_{config_hash}", self.default_model, results)
        yield {"event" : "final" , "data" : cast(ApplicantResumeDTO , results)}
