from typing import Protocol
from mawhub.app.job.repo.job_opening_repo import JobOpeningRepo, JobOpeningRepoInterface
from mawhub.app.job.repo.job_pipeline_repo import JobPipelineRepo, JobPipelineRepoInterface
from mawhub.app.job.repo.parsed_document_repo import ParsedDocumentRepoInterface,ParsedDocumentRepo
class JobRepoInterface(Protocol):
    job_opening: JobOpeningRepoInterface
    job_pipeline: JobPipelineRepoInterface
    parsed_document : ParsedDocumentRepoInterface

class JobRepo:
    job_opening: JobOpeningRepoInterface
    job_pipeline: JobPipelineRepoInterface
    parsed_document : ParsedDocumentRepoInterface

    def __init__(
        self,
    ):
        self.job_opening = JobOpeningRepo()
        self.job_pipeline= JobPipelineRepo()
        self.parsed_document = ParsedDocumentRepo()

