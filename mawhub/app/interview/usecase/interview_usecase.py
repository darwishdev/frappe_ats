from typing import Protocol

from mawhub.agent.question_bank_personalizer.question_bank_personlaizer_agent import QuestionBankPersonalizerAgent
from mawhub.app.interview.adapter.interview_adapter import InterviewAdapter, InterviewAdapterInterface
from mawhub.app.interview.repo.interview_repo import  InterviewRepoInterface
from mawhub.app.interview.usecase.interview_interview_usecase import InterviewInterviewUsecase, InterviewInterviewUsecaseInterface
from mawhub.app.interview.usecase.interview_question_bank_usecase import InterviewQuestionBankUsecase, InterviewQuestionBankUsecaseInterface

class InterviewUsecaseInterface(Protocol):
    interview: InterviewInterviewUsecaseInterface
    question_bank: InterviewQuestionBankUsecaseInterface

class InterviewUsecase:
    interview: InterviewInterviewUsecaseInterface
    question_bank: InterviewQuestionBankUsecaseInterface
    adapter: InterviewAdapterInterface
    def __init__(
        self,
        repo: InterviewRepoInterface,
        question_bank_personalizer_agent: QuestionBankPersonalizerAgent,
        ):
        adapter = InterviewAdapter()
        self.interview = InterviewInterviewUsecase(repo)
        self.question_bank = InterviewQuestionBankUsecase(repo,adapter,question_bank_personalizer_agent)


