
# mawhub/app/job/dto/job_opening.py
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
from typing import Dict, Iterator, List, Literal, Optional, TypedDict, cast
from google.genai import types, Client
from pydantic import BaseModel, Field

from mawhub.app.job.agent.resume_parser_agent import AgentEvent


class JobMeta(BaseModel):
    title: str
    company: str
    location: Optional[str]
    reports_to: Optional[str]


class ResponsibilityList(BaseModel):
    items: List[str]


class RequirementList(BaseModel):
    items: List[str]


class QualificationList(BaseModel):
    items: List[str]


class KPIList(BaseModel):
    items: List[str]


class JobOpeningAgentDTO(BaseModel):
    meta: Optional[JobMeta]
    summary: Optional[str]
    responsibilities: Optional[List[str]]
    requirements: Optional[List[str]]
    qualifications: Optional[List[str]]
    kpis: Optional[List[str]]
    benefits: Optional[str]
class JobSection(BaseModel):
    name: str = Field(
        description=(
            "One of: 'meta', 'summary', 'responsibilities', "
            "'requirements', 'qualifications', 'kpis', 'benefits'"
        )
    )
    content: str


class ChunkedJobDescription(BaseModel):
    sections: List[JobSection]

class JobAgentSection(TypedDict):
    name: str
    content: str


class JobAgentEvent(TypedDict):
    event: Literal["update", "final", "error"]
    data: JobOpeningAgentDTO | JobAgentSection | str

class JobOpeningWorkflow:
    def __init__(
        self,
        client:Client,
        model_name: str,
        get_cache_fn,
        set_cache_fn
    ):
        self.client = client
        self.default_model = model_name
        self.get_cache_fn = get_cache_fn
        self.set_cache_fn = set_cache_fn

    def get_text_hash(self, text: str) -> str:
        return hashlib.sha256(text.strip().encode()).hexdigest()

    def agent_meta_labeler(self, raw_text: str, model_id: str) -> ChunkedJobDescription:
        prompt = f"""
Analyze the following job description and split it into structured sections.

Sections:
- meta (title, company, location, reports_to)
- summary
- responsibilities
- requirements
- qualifications
- kpis
- benefits

Text:
{raw_text}
"""

        response = self.client.models.generate_content(
            model=model_id,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ChunkedJobDescription
            )
        )

        return cast(ChunkedJobDescription, response.parsed)
    def extraction_worker(self, section_name: str, text: str, schema, model_id: str):
        is_plain_text = schema is str

        prompt = f"Extract structured {section_name} from the following text:\n\n{text}"

        response = self.client.models.generate_content(
            model=model_id,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="text/plain" if is_plain_text else "application/json",
                response_schema=None if is_plain_text else schema
            )
        )

        if is_plain_text:
            return response.text.strip() if response.text else ""

        res = response.parsed

        if hasattr(res, "items"):
            return [i for i in getattr(res,"items")]

        if isinstance(res,BaseModel):
            return res.model_dump()
        return res
    def run(
        self,
        job_text: str,
        model_overrides: Optional[Dict[str, str]] = None
    ) ->Iterator[JobAgentEvent]:
        overrides = model_overrides or {}

        def get_model(step: str) -> str:
            return overrides.get(step, self.default_model)

        text_hash = self.get_text_hash(job_text)
        config_hash = hashlib.md5(json.dumps(overrides, sort_keys=True).encode()).hexdigest()
        cache_key = f"{text_hash}_{config_hash}"

        if self.get_cache_fn:
            cached = self.get_cache_fn(cache_key, self.default_model)
            if cached:
                yield {"event": "final", "data": json.loads(cached)}
                return

        # 1️⃣ Label JD
        chunked = self.agent_meta_labeler(job_text, get_model("labeler"))

        schema_map = {
            "meta": JobMeta,
            "summary": str,
            "responsibilities": ResponsibilityList,
            "requirements": RequirementList,
            "qualifications": QualificationList,
            "kpis": KPIList,
            "benefits": str,
        }

        results = {}

        with ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(
                    self.extraction_worker,
                    section.name,
                    section.content,
                    schema_map[section.name],
                    get_model(section.name)
                ): section.name
                for section in chunked.sections
                if section.name in schema_map
            }

            for future in as_completed(futures):
                section_name = futures[future]
                try:
                    data = future.result()
                    results[section_name] = data

                    yield {
                        "event": "update",
                        "data": {
                            "name": section_name,
                            "content": json.dumps(data)
                        }
                    }
                except Exception as e:
                    yield {"event": "error", "data": str(e)}

        if self.set_cache_fn:
            self.set_cache_fn(cache_key, self.default_model, results)

        yield {"event": "final", "data": cast(JobOpeningAgentDTO, results)}
