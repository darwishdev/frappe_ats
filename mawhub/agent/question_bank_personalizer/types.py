from typing import List, Literal, Optional
from pydantic import BaseModel, Field


# --- Shared Sub-models ---

class FollowupTrigger(BaseModel):
    condition: str = Field(description="Condition string e.g. 'if_mentions_WebSocket'")
    follow_up: str = Field(description="Follow-up question to ask if condition is met")


class EvaluationCriteria(BaseModel):
    must_mention: str = Field(
        description="Newline-separated concepts the candidate must mention to pass"
    )
    bonus_points: str = Field(
        description="Newline-separated advanced concepts that earn bonus points"
    )


# --- Question Bank Question (mirrors ERPNext DocType exactly) ---

class QuestionBankQuestion(BaseModel):
    name: str = Field(description="Unique question ID e.g. TLQ001")
    doctype: Literal["Question Bank Question"] = Field(
        default="Question Bank Question"
    )
    category: str = Field(description="Question category e.g. System Design")
    difficulty: Literal["Easy", "Medium", "Hard"] = Field(
        description="Question difficulty level"
    )
    estimated_time_minutes: int = Field(
        description="Estimated time to answer in minutes"
    )
    question: str = Field(description="The question text")
    ideal_answer_keywords: str = Field(
        description="Newline-separated keywords expected in an ideal answer"
    )
    evaluation_criteria: List[EvaluationCriteria] = Field(
        description="Single-item list containing must_mention and bonus_points"
    )
    followup_triggers: List[FollowupTrigger] = Field(
        default_factory=list,
        description="Conditional follow-up triggers based on candidate response"
    )
    pass_treshold: float = Field(
        description="Minimum score (0.0-1.0) to consider question passed"
    )


# --- Personalized Output (same shape + personalization metadata) ---

class PersonalizedQuestionBankQuestion(BaseModel):
    name: str = Field(description="Same ID as the original question e.g. TLQ001")
    doctype: Literal["Question Bank Question"] = Field(
        default="Question Bank Question"
    )
    category: str
    difficulty: Literal["Easy", "Medium", "Hard"]
    estimated_time_minutes: int
    question: str = Field(
        description="Personalized question referencing candidate's specific background"
    )
    ideal_answer_keywords: str = Field(
        description="Newline-separated keywords, possibly updated for candidate context"
    )
    evaluation_criteria: List[EvaluationCriteria]
    followup_triggers: List[FollowupTrigger] = Field(default_factory=list)
    pass_treshold: float
    # Personalization metadata
    personalization_reason: str = Field(
        description="Why this question was personalized, or 'no_change' if left unchanged"
    )
    relevance_score: float = Field(
        description="How relevant this question is to the candidate (0.0-1.0)"
    )


class PersonalizedQuestionBankModel(BaseModel):
    questions: List[PersonalizedQuestionBankQuestion] = Field(
        description=(
            "Personalized questions in the same count as input, "
            "ordered by relevance to candidate descending."
        )
    )


# --- Agent Inputs ---

class CandidateProfile(BaseModel):
    applicant_name: str
    job_title: str
    years_experience: Optional[int] = None
    primary_skills: List[str]
    certifications: List[str] = Field(default_factory=list)
    summary: str = ""


class JobObjectives(BaseModel):
    role_title: str
    must_have_skills: List[str]
    nice_to_have_skills: List[str] = Field(default_factory=list)
    seniority_level: Literal["Junior", "Mid", "Senior", "Lead", "Principal"]
