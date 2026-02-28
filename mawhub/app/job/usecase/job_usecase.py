from typing import Protocol
from mawhub.agent.document_parser.document_parser_agent import DocumentParserWorkflow
from mawhub.agent.file_text_parser.file_text_parser_agent import FileTextParserWorkflow
from mawhub.agent.job_opening_parser.job_opening_parser_agent import JobOpeningParserWorkflow
from mawhub.app.job.repo.job_repo import JobRepoInterface
from mawhub.app.job.usecase.job_opening_usecase import JobOpeningUsecase, JobOpeningUsecaseInterface
from mawhub.app.job.usecase.job_pipeline_usecase import JobPipelineUsecase, JobPipelineUsecaseInterface
from mawhub.app.job.usecase.parsed_document_usecase import ParsedDocumentUsecase, ParsedDocumentUsecaseInterface

class JobUseCaseInterface(Protocol):
    job_opening: JobOpeningUsecaseInterface
    job_pipeline: JobPipelineUsecaseInterface
    parsed_document: ParsedDocumentUsecaseInterface
    file_text_parser_agent: FileTextParserWorkflow

class JobUseCase:
    job_opening: JobOpeningUsecaseInterface
    job_pipeline: JobPipelineUsecaseInterface
    parsed_document: ParsedDocumentUsecaseInterface
    file_text_parser_agent: FileTextParserWorkflow
    def __init__(
        self,
        job_repo: JobRepoInterface,
        job_opening_parser_agent: JobOpeningParserWorkflow,
        document_parser_agent: DocumentParserWorkflow,
        file_text_parser_agent: FileTextParserWorkflow,
    ):
        self.job_opening = JobOpeningUsecase(job_repo,job_opening_parser_agent)
        self.job_pipeline= JobPipelineUsecase(job_repo)
        self.parsed_document = ParsedDocumentUsecase(job_repo,document_parser_agent,file_text_parser_agent)
        self.file_text_parser_agent = file_text_parser_agent


