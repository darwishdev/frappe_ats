from typing import Protocol


from mawhub.app.job.agent.document_parser.document_parser_agent import DocumentParserWorkflow
from mawhub.app.job.agent.job_opening_parser.job_opening_parser_agent import JobOpeningParserWorkflow
from mawhub.app.job.agent.resume_parser.resume_parser_agent import ResumeWorkflow
from mawhub.app.job.repo.job_repo import JobRepoInterface
from mawhub.app.job.usecase.applicant_resume_usecase import ApplicantResumeUsecase, ApplicantResumeUsecaseInterface
# from mawhub.app.job.usecase.auth_usecase import AuthUsecase, AuthUsecaseInterface
from mawhub.app.job.usecase.job_applicant_usecase import JobApplicantUsecase, JobApplicantUsecaseInterface
from mawhub.app.job.usecase.job_opening_usecase import JobOpeningUsecase, JobOpeningUsecaseInterface
from mawhub.app.job.usecase.job_pipeline_usecase import JobPipelineUsecase, JobPipelineUsecaseInterface
from mawhub.app.job.usecase.parsed_document_usecase import ParsedDocumentUsecase, ParsedDocumentUsecaseInterface

class JobUseCaseInterface(Protocol):
    job_opening: JobOpeningUsecaseInterface
    job_applicant: JobApplicantUsecaseInterface
    job_pipeline: JobPipelineUsecaseInterface
    parsed_document: ParsedDocumentUsecaseInterface
    applicant_resume: ApplicantResumeUsecaseInterface

class JobUseCase:
    job_opening: JobOpeningUsecaseInterface
    job_applicant: JobApplicantUsecaseInterface
    job_pipeline: JobPipelineUsecaseInterface
    applicant_resume: ApplicantResumeUsecaseInterface
    parsed_document: ParsedDocumentUsecaseInterface
    def __init__(
        self,
        job_repo: JobRepoInterface,
        resume_parser_agent: ResumeWorkflow,
        job_opening_parser_agent: JobOpeningParserWorkflow,
        document_parser_agent: DocumentParserWorkflow,
    ):
        self.job_opening = JobOpeningUsecase(job_repo,job_opening_parser_agent)
        self.job_pipeline= JobPipelineUsecase(job_repo)
        self.parsed_document = ParsedDocumentUsecase(job_repo,document_parser_agent)
        self.job_applicant = JobApplicantUsecase(job_repo)
        self.applicant_resume = ApplicantResumeUsecase(job_repo , resume_parser_agent)


