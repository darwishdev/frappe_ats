import hashlib
import json
from time import sleep
from typing import Optional, TypedDict, cast
from pydantic import BaseModel, Field
from google.genai import types, Client
from typing import  Optional, Callable
# ----------------------------
# LLM Schema for JobOpening Extraction (fully documented)
# ----------------------------
class JobOpeningSchema(BaseModel):
    job_title: str = Field(
        ...,
        description="The title of the job opening, e.g., 'Software Engineer', 'Product Manager'."
    )
    designation: Optional[str] = Field(
        default=None,
        description="The role or level of the position, e.g., 'Senior', 'Junior', 'Lead'."
    )
    customer: Optional[str] = Field(
        default=None,
        description="The name of the company offering the job."
    )
    location: Optional[str] = Field(
        default=None,
        description="The geographical location of the job (city, country, remote status)."
    )
    planned_vacancies: int = Field(
        default=1,
        description="The planned number of positions intended to be filled."
    )
    vacancies: int = Field(
        default=1,
        description="The actual number of open positions currently available."
    )
    lower_range: float = Field(
        default=0.0,
        description="The minimum salary for the position (numerical, in company's currency)."
    )
    upper_range: float = Field(
        default=0.0,
        description="The maximum salary for the position (numerical, in company's currency)."
    )


# ----------------------------
# TypedDict for final event output
# ----------------------------
class JobOpeningEvent(TypedDict):
    job_title: str
    designation: Optional[str]
    customer: Optional[str]
    location: Optional[str]
    planned_vacancies: int
    vacancies: int
    lower_range: float
    upper_range: float

class JobOpeningParserWorkflow:
    """
    Single-step LLM workflow:
    Converts a ParsedDocumentFinalEvent into a JobOpeningEvent.
    """

    def __init__(
            self,
             client: Client,
             model_name: str,
             get_cache_fn: Optional[Callable[[str, str], Optional[str]]] = None,
             set_cache_fn: Optional[Callable[[str, str, dict], None]] = None
     ):
        self.client = client
        self.default_model = model_name
        self.get_cache_fn = get_cache_fn
        self.set_cache_fn = set_cache_fn
    def job_opening_schema_to_event(self,schema: JobOpeningSchema) -> JobOpeningEvent:
        """Converts JobOpeningSchema (Pydantic) to JobOpeningEvent (TypedDict)"""
        return {
            "job_title": schema.job_title,
            "designation": schema.designation,
            "customer": schema.customer,
            "location": schema.location,
            "planned_vacancies": schema.planned_vacancies,
            "vacancies": schema.vacancies,
            "lower_range": schema.lower_range,
            "upper_range": schema.upper_range,
        }

    def get_text_hash(self, text: str) -> str:
        return hashlib.sha256(text.strip().encode("utf-8")).hexdigest()
    def run(self, full_text: str) -> JobOpeningEvent:
        """
        final_event: ParsedDocumentFinalEvent
        Returns: JobOpeningEvent TypedDict
        """
        prompt = f"""
You are an AI assistant that extracts job opening information from a fully parsed document.
The file text is:
{full_text}

Task:
- Extract all relevant information to create a job opening.
- Return ONLY a JSON object with these fields:
  job_title, designation, company, location, planned_vacancies,
  vacancies, lower_range, upper_range, publish, publish_salary_range, publish_applications_received
- If values are missing, use defaults: 1 for publish, publish_salary_range, publish_applications_received
- Ensure the JSON matches the JobOpeningSchema.
"""

        try:
            cache_key = self.get_text_hash(full_text) + "job_opening_parser_agent"
            cache_model = self.default_model
            if self.get_cache_fn:
                print("cache caclllaeddd")
                cached = self.get_cache_fn(cache_key, cache_model)
                if isinstance(cached,str):
                    cached = json.loads(cached)
                if cached:
                    return cached
            response = self.client.models.generate_content(
                model=self.default_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=JobOpeningSchema,
                    temperature=0,
                )
            )
            parsed_resp = cast(JobOpeningSchema, response.parsed)
            response = self.job_opening_schema_to_event(parsed_resp)

            try:
                if self.set_cache_fn:
                    self.set_cache_fn(cache_key, cache_model, response)
            except Exception as e:
                pass
            return response

        except Exception as e:
            raise ValueError(f"LLM output could not be parsed as JobOpening: {str(e)}")
