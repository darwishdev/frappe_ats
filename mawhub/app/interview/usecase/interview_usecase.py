from typing import Protocol

from mawhub.app.interview.repo.interview_repo import  InterviewRepoInterface
from mawhub.app.interview.usecase.interview_interview_usecase import InterviewInterviewUsecase, InterviewInterviewUsecaseInterface

class InterviewUsecaseInterface(Protocol):
    interview: InterviewInterviewUsecaseInterface

class InterviewUsecase:
    interview: InterviewInterviewUsecaseInterface
    def __init__(
        self,
        repo: InterviewRepoInterface,
        ):
        self.interview = InterviewInterviewUsecase(repo)


