from typing import Protocol

from frappe.model.document import Document

from mawhub.app.interview.repo.interview_interview_repo import InterviewDBModel, InterviewListFilter, InterviewListItem
from mawhub.app.interview.repo.interview_repo import InterviewRepoInterface


class InterviewInterviewUsecaseInterface(Protocol):
    def interview_create_update(self, payload: InterviewDBModel) -> Document: ...
    def interview_find(self, name: str) -> dict: ...
    def interview_list(self, filters: InterviewListFilter) -> list[InterviewListItem]: ...


class InterviewInterviewUsecase:
    repo: InterviewRepoInterface
    def __init__(
        self,
        repo: InterviewRepoInterface,
    ):
        self.repo = repo

    def interview_create_update(self, payload: InterviewDBModel) -> Document:
        return self.repo.interview.create_or_update(payload)

    def interview_find(self, name: str) -> dict:
        return self.repo.interview.interview_find(name)

    def interview_list(self, filters: InterviewListFilter) -> list[InterviewListItem]:
        return self.repo.interview.interview_list(filters)
