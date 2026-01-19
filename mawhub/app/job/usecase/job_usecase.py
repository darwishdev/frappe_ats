from typing import Protocol

from mawhub.app.job.repo.job_repo import JobRepoInterface
from mawhub.app.job.usecase.auth_usecase import AuthUsecase, AuthUsecaseInterface
from mawhub.app.job.usecase.interview_usecase import InterviewUsecase, InterviewUsecaseInterface
from mawhub.app.job.usecase.job_applicant_usecase import JobApplicantUsecase, JobApplicantUsecaseInterface
from mawhub.app.job.usecase.job_opening_usecase import JobOpeningUsecase, JobOpeningUsecaseInterface

class JobUseCaseInterface(Protocol):
    job_opening: JobOpeningUsecaseInterface
    job_applicant: JobApplicantUsecaseInterface
    interview: InterviewUsecaseInterface
    auth: AuthUsecaseInterface

class JobUseCase:
    job_opening: JobOpeningUsecaseInterface
    job_applicant: JobApplicantUsecaseInterface
    interview: InterviewUsecaseInterface
    auth: AuthUsecaseInterface
    def __init__(
        self,
        job_repo: JobRepoInterface,
    ):
        self.job_opening = JobOpeningUsecase(job_repo)
        self.job_applicant = JobApplicantUsecase(job_repo)
        self.interview = InterviewUsecase(job_repo)
        self.auth = AuthUsecase(job_repo)


