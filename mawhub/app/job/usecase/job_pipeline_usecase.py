from typing import Protocol
from frappe.model.document import Document
from mawhub.app.job.repo.job_repo import JobRepoInterface
from mawhub.mawhub.doctype.job_pipeline.job_pipeline import JobPipelineDBModel

class JobPipelineUsecaseInterface(Protocol):
	def job_pipeline_create_update(self, payload: JobPipelineDBModel)->Document: ...

class JobPipelineUsecase:
    repo: JobRepoInterface
    def __init__(
        self,
        repo: JobRepoInterface,
    ):
        self.repo = repo

    def job_pipeline_create_update(self, payload: JobPipelineDBModel)->Document:
        return self.repo.job_pipeline.create_or_update(payload)

