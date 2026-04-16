from typing import List, Literal, Optional
from pydantic import BaseModel, Field

from mawhub.agent.question_bank_personalizer.types import QuestionBankQuestion


class JobInfo(BaseModel):
    role_title: str = Field(description="The job title / role name")
    seniority_level: Literal["Junior", "Mid", "Senior", "Lead", "Principal"] = Field(
        default="Mid",
        description="Seniority level of the role"
    )
    must_have_skills: List[str] = Field(
        default_factory=list,
        description="Skills explicitly required for the role"
    )
    nice_to_have_skills: List[str] = Field(
        default_factory=list,
        description="Skills that are a plus but not required"
    )
    description: Optional[str] = Field(
        default=None,
        description="Raw job description text to help infer required skills and context"
    )


class GeneratedQuestionBankModel(BaseModel):
    questions: List[QuestionBankQuestion] = Field(
        description=(
            "Freshly generated interview questions for the given job, "
            "ordered from most critical to least critical for the role."
        )
    )
