from typing import Protocol
from mawhub.app.applicant.repo.applicant_resume_repo import ApplicantResumeRepo, ApplicantResumeRepoInterface
from mawhub.app.applicant.repo.job_applicant_repo import JobApplicantRepo, JobApplicantRepoInterface
class ApplicantRepoInterface(Protocol):
    job_applicant: JobApplicantRepoInterface
    applicant_resume : ApplicantResumeRepoInterface

class ApplicantRepo:
    job_applicant: JobApplicantRepoInterface
    applicant_resume : ApplicantResumeRepoInterface

    def __init__(
        self,
    ):
        self.job_applicant = JobApplicantRepo()
        self.applicant_resume = ApplicantResumeRepo()

