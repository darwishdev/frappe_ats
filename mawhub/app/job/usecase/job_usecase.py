from typing import Protocol
from mawhub.agent.document_parser.document_parser_agent import DocumentParserWorkflow
from mawhub.agent.file_text_parser.file_text_parser_agent import FileTextParserWorkflow
from mawhub.agent.job_opening_parser.job_opening_parser_agent import JobOpeningParserWorkflow
from mawhub.agent.question_bank_maker.question_bank_maker_agent import QuestionBankMakerAgent
from mawhub.app.applicant.repo.applicant_repo import ApplicantRepoInterface
from mawhub.app.interview.repo.interview_repo import InterviewRepoInterface
from mawhub.app.job.adapter.job_adapter import JobAdapter
from mawhub.app.job.repo.job_repo import JobRepoInterface
from mawhub.app.job.usecase.job_opening_usecase import JobOpeningUsecase, JobOpeningUsecaseInterface
from mawhub.app.job.usecase.job_pipeline_usecase import JobPipelineUsecase, JobPipelineUsecaseInterface
from mawhub.app.job.usecase.job_workable_usecase import JobWorkableUsecase, JobWorkableUsecaseInterface
from mawhub.app.job.usecase.job_workable_native_sync_usecase import (
    JobWorkableNativeSyncUsecase,
    JobWorkableNativeSyncUsecaseInterface,
)
from mawhub.app.job.usecase.parsed_document_usecase import ParsedDocumentUsecase, ParsedDocumentUsecaseInterface
from mawhub.pkg.workable.workable_client import WorkableApiClient

class JobUseCaseInterface(Protocol):
    job_opening: JobOpeningUsecaseInterface
    job_pipeline: JobPipelineUsecaseInterface
    parsed_document: ParsedDocumentUsecaseInterface
    workable: JobWorkableUsecaseInterface
    native_sync: JobWorkableNativeSyncUsecaseInterface
    file_text_parser_agent: FileTextParserWorkflow

class JobUseCase:
    job_opening: JobOpeningUsecaseInterface
    job_pipeline: JobPipelineUsecaseInterface
    parsed_document: ParsedDocumentUsecaseInterface
    workable: JobWorkableUsecaseInterface
    native_sync: JobWorkableNativeSyncUsecaseInterface
    file_text_parser_agent: FileTextParserWorkflow
    workable_client: WorkableApiClient

    def __init__(
        self,
        job_repo: JobRepoInterface,
        job_opening_parser_agent: JobOpeningParserWorkflow,
        document_parser_agent: DocumentParserWorkflow,
        file_text_parser_agent: FileTextParserWorkflow,
        workable_client: WorkableApiClient,
        question_bank_maker_agent: QuestionBankMakerAgent,
        applicant_repo: ApplicantRepoInterface,
        interview_repo: InterviewRepoInterface,
    ):
        adapter = JobAdapter()
        job_opening_usecase = JobOpeningUsecase(job_repo, job_opening_parser_agent, question_bank_maker_agent)

        self.workable = JobWorkableUsecase(job_repo, adapter, workable_client)
        self.job_opening = job_opening_usecase
        self.job_pipeline = JobPipelineUsecase(job_repo)
        self.parsed_document = ParsedDocumentUsecase(job_repo, document_parser_agent, file_text_parser_agent)
        self.native_sync = JobWorkableNativeSyncUsecase(
            repo=job_repo,
            applicant_repo=applicant_repo,
            interview_repo=interview_repo,
            adapter=adapter,
            job_opening_usecase=job_opening_usecase,
        )
        self.file_text_parser_agent = file_text_parser_agent


