from frappe import _
from typing import List, Protocol
from mawhub.app.job.dto.job_opening import JobOpeningDTO, job_opening_list_sql_to_dto, job_opening_sql_to_dto
from mawhub.app.job.repo.job_repo import  JobRepoInterface


class JobOpeningUsecaseInterface(Protocol):
    def job_opening_list(
        self,
        user_name: str,
    ) -> List[JobOpeningDTO]: ...
    def job_opening_find(
        self,
        job: str,
    ) -> JobOpeningDTO: ...
class JobOpeningUsecase:
    repo: JobRepoInterface
    def __init__(
        self,
        repo: JobRepoInterface,
    ):
        self.repo = repo

    def job_opening_list(
        self,
        user_name: str,
    ) -> List[JobOpeningDTO]:
        db_rows = self.repo.job_opening.job_opening_list(user_name)
        return job_opening_list_sql_to_dto(db_rows)

    def job_opening_find(
        self,
        job: str,
    ) -> JobOpeningDTO:
        db_rows = self.repo.job_opening.job_opening_find(job)
        return job_opening_sql_to_dto(db_rows)
