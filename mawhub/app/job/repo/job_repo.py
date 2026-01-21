from typing import Protocol
from mawhub.app.job.repo.applicant_resume_repo import ApplicantResumeRepo, ApplicantResumeRepoInterface
from mawhub.app.job.repo.auth_repo import AuthRepo, AuthRepoInterface
from mawhub.app.job.repo.interview_repo import InterviewRepo, InterviewRepoInterface
from mawhub.app.job.repo.job_applicant_repo import JobApplicantRepo, JobApplicantRepoInterface
from mawhub.app.job.repo.job_opening_repo import JobOpeningRepo, JobOpeningRepoInterface
class JobRepoInterface(Protocol):
    job_opening: JobOpeningRepoInterface
    job_applicant: JobApplicantRepoInterface
    interview: InterviewRepoInterface
    auth: AuthRepoInterface
    applicant_resume : ApplicantResumeRepoInterface

class JobRepo:
    job_opening: JobOpeningRepoInterface
    job_applicant: JobApplicantRepoInterface
    interview: InterviewRepoInterface
    auth: AuthRepoInterface
    applicant_resume : ApplicantResumeRepoInterface
    def __init__(
        self,
    ):
        self.job_opening = JobOpeningRepo()
        self.job_applicant = JobApplicantRepo()
        self.interview = InterviewRepo()
        self.auth = AuthRepo()
        self.applicant_resume = ApplicantResumeRepo()

