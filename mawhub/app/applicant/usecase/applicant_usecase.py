from typing import Protocol
from mawhub.agent.resume_parser.resume_parser_agent import ResumeWorkflow
from mawhub.app.applicant.repo.applicant_repo import ApplicantRepo, ApplicantRepoInterface
from mawhub.agent.file_text_parser.file_text_parser_agent import FileTextParserWorkflow
from mawhub.app.applicant.usecase.applicant_resume_usecase import ApplicantResumeUsecase, ApplicantResumeUsecaseInterface
from mawhub.app.applicant.usecase.job_applicant_usecase import JobApplicantUsecase, JobApplicantUsecaseInterface

class ApplicantUsecaseInterface(Protocol):
    job_applicant: JobApplicantUsecaseInterface
    file_text_parser_agent: FileTextParserWorkflow
    applicant_resume: ApplicantResumeUsecaseInterface

class ApplicantUsecase:
    job_applicant: JobApplicantUsecaseInterface
    applicant_resume: ApplicantResumeUsecaseInterface
    file_text_parser_agent: FileTextParserWorkflow
    def __init__(
        self,
        repo: ApplicantRepo,
        resume_parser_agent: ResumeWorkflow,
        file_text_parser_agent: FileTextParserWorkflow,
        ):
        self.job_applicant = JobApplicantUsecase(repo)
        self.applicant_resume = ApplicantResumeUsecase(repo , resume_parser_agent,file_text_parser_agent)
        self.file_text_parser_agent = file_text_parser_agent


