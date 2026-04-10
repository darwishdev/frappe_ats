from typing import Protocol

from mawhub.app.interview.repo.interview_interview_repo import InterviewInterviewRepo, InterviewInterviewRepoInterface
from mawhub.app.interview.repo.interview_question_bank_repo import InterviewQuestionBankRepo, InterviewQuestionBankRepoInterface

class InterviewRepoInterface(Protocol):
    interview: InterviewInterviewRepoInterface
    question_bank: InterviewQuestionBankRepoInterface

class InterviewRepo:
    interview: InterviewInterviewRepoInterface
    question_bank: InterviewQuestionBankRepoInterface
    def __init__(
        self,
    ):
        self.interview = InterviewInterviewRepo()
        self.question_bank = InterviewQuestionBankRepo()

