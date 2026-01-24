from typing import Protocol

from mawhub.app.job.agent.job_opening_parser import JobOpeningWorkflow
from mawhub.app.job.agent.resume_parser_agent import ResumeWorkflow
from mawhub.app.job.repo.job_repo import JobRepoInterface
from mawhub.app.job.usecase.applicant_resume_usecase import ApplicantResumeUsecase, ApplicantResumeUsecaseInterface
from mawhub.app.job.usecase.auth_usecase import AuthUsecase, AuthUsecaseInterface
from mawhub.app.job.usecase.interview_usecase import InterviewUsecase, InterviewUsecaseInterface
from mawhub.app.job.usecase.job_applicant_usecase import JobApplicantUsecase, JobApplicantUsecaseInterface
from mawhub.app.job.usecase.job_opening_usecase import JobOpeningUsecase, JobOpeningUsecaseInterface
from mawhub.pkg.sql.cache_utils import get_ai_cache, set_ai_cache

class JobUseCaseInterface(Protocol):
    job_opening: JobOpeningUsecaseInterface
    job_applicant: JobApplicantUsecaseInterface
    interview: InterviewUsecaseInterface
    auth: AuthUsecaseInterface
    applicant_resume: ApplicantResumeUsecaseInterface
    resume_agent: ResumeWorkflow

class JobUseCase:
    job_opening: JobOpeningUsecaseInterface
    job_applicant: JobApplicantUsecaseInterface
    interview: InterviewUsecaseInterface
    auth: AuthUsecaseInterface
    applicant_resume: ApplicantResumeUsecaseInterface
    resume_agent: ResumeWorkflow
    job_agent: JobOpeningWorkflow
    def __init__(
        self,
        gemini_api_key:str,
        job_repo: JobRepoInterface,
    ):
        model_name = 'gemini-2.5-flash-lite'
        resume_agent = ResumeWorkflow(api_key=gemini_api_key,model_name=model_name , get_cache_fn=get_ai_cache ,set_cache_fn=set_ai_cache)
        job_agent = JobOpeningWorkflow(api_key=gemini_api_key,model_name=model_name , get_cache_fn=get_ai_cache ,set_cache_fn=set_ai_cache)
        self.resume_agent = resume_agent
        self.job_agent = job_agent
        self.job_opening = JobOpeningUsecase(job_repo,job_agent)
        self.job_applicant = JobApplicantUsecase(job_repo)
        self.interview = InterviewUsecase(job_repo)
        self.auth = AuthUsecase(job_repo)
        self.applicant_resume = ApplicantResumeUsecase(job_repo , resume_agent)


