from typing import NotRequired, TypedDict


# ── Question Bank ──────────────────────────────────────────────────────────────

class FollowupTrigger(TypedDict):
    condition: str
    follow_up: str


class EvaluationCriteria(TypedDict):
    must_mention: list[str]
    bonus_points: list[str]


class Question(TypedDict):
    id: str
    category: str
    difficulty: str
    estimated_time_minutes: int
    question: str
    ideal_answer_keywords: list[str]
    evaluation_criteria: list[EvaluationCriteria]
    followup_triggers: list[FollowupTrigger]
    pass_threshold: float


class QuestionBank(TypedDict):
    name: str
    focus_areas: list[str]
    questions: list[Question]


# ── Candidate ─────────────────────────────────────────────────────────────────

class CandidateExperience(TypedDict):
    company: str
    role: str
    from_date: str  # key is "from" in the raw dict — adapter handles remapping
    to_date: str    # key is "to" in the raw dict — adapter handles remapping
    responsibilities: list[str]


class CandidateEducation(TypedDict):
    degree: str
    institution: str
    year: str


class CandidateProject(TypedDict):
    name: str
    description: list[str]


class Candidate(TypedDict):
    name: str
    email: str
    phone: str
    designation: str
    summary: str
    skills: list[str]
    experience: list[CandidateExperience]
    education: list[CandidateEducation]
    projects: list[CandidateProject]


# ── Job ───────────────────────────────────────────────────────────────────────

class JobDescriptionSection(TypedDict):
    title: str
    description: str
    points: list[str]


class PipelineStep(TypedDict):
    code: str
    name: str
    type: str


class Job(TypedDict):
    id: str
    title: str
    designation: str
    department: str
    location: str
    description: list[JobDescriptionSection]
    current_pipeline_step: NotRequired[PipelineStep]


# ── Interview Round ───────────────────────────────────────────────────────────

class ExpectedSkill(TypedDict):
    skill: str
    description: str


class Round(TypedDict):
    name: str
    type: str
    designation: str
    expected_average_rating: float
    expected_skills: list[ExpectedSkill]


# ── Interview (root) ──────────────────────────────────────────────────────────

class Interview(TypedDict):
    id: str
    scheduled_on: str
    designation: str
    expected_average_rating: float
    status: str


# ── Full interview_find() response ────────────────────────────────────────────

class InterviewFindResult(TypedDict):
    interview: Interview
    candidate: Candidate
    job: Job
    round: Round
    question_bank: QuestionBank
