from typing import Protocol
from mawhub.app.job.repo.auth_repo import AuthRepo, AuthRepoInterface
from mawhub.app.job.repo.interview_repo import InterviewRepo, InterviewRepoInterface
from mawhub.app.job.repo.job_applicant_repo import JobApplicantRepo, JobApplicantRepoInterface
from mawhub.app.job.repo.job_opening_repo import JobOpeningRepo, JobOpeningRepoInterface
class JobRepoInterface(Protocol):
    job_opening: JobOpeningRepoInterface
    job_applicant: JobApplicantRepoInterface
    interview: InterviewRepoInterface
    auth: AuthRepoInterface

class JobRepo:
    job_opening: JobOpeningRepoInterface
    job_applicant: JobApplicantRepoInterface
    interview: InterviewRepoInterface
    auth: AuthRepoInterface
    def __init__(
        self,
    ):
        job_opening = JobOpeningRepo()
        job_applicant = JobApplicantRepo()
        interview = InterviewRepo()
        auth = AuthRepo()
        self.job_opening = job_opening
        self.auth = auth
        self.interview = interview
        self.job_applicant = job_applicant

