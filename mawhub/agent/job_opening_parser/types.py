import hashlib
import json
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


