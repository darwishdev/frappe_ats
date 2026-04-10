from typing import Protocol

from mawhub.agent.question_bank_personalizer.types import (
    CandidateProfile,
    JobObjectives,
    PersonalizedQuestionBankQuestion,
    QuestionBankQuestion,
)
from mawhub.app.interview.repo.interview_types import (
    Candidate,
    InterviewFindResult,
    Job,
    QuestionBank,
    Round,
)


class InterviewAdapterInterface(Protocol):
    interview: "InterviewInterviewAdapterInterface"


class InterviewInterviewAdapterInterface(Protocol):
    def parse_interview_result(self, raw: dict) -> InterviewFindResult: ...
    def to_candidate_profile(self, candidate: Candidate) -> CandidateProfile: ...
    def to_job_objectives(self, job: Job, round_: Round) -> JobObjectives: ...
    def to_question_bank_questions(self, question_bank: QuestionBank) -> list[QuestionBankQuestion]: ...


class InterviewAdapter:
    interview: "InterviewInterviewAdapterInterface"

    def __init__(self) -> None:
        from mawhub.app.interview.adapter.interview_interview_adapter import InterviewInterviewAdapter
        self.interview = InterviewInterviewAdapter()
