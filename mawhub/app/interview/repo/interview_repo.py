from typing import Protocol

from mawhub.app.interview.repo.interview_interview_repo import InterviewInterviewRepo, InterviewInterviewRepoInterface

class InterviewRepoInterface(Protocol):
    interview: InterviewInterviewRepoInterface

class InterviewRepo:
    interview: InterviewInterviewRepoInterface

    def __init__(
        self,
    ):
        self.interview = InterviewInterviewRepo()

