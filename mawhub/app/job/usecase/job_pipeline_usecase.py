from typing import Protocol, cast
from frappe.model.document import Document
from mawhub.app.job.dto.job_pipeline_dto import JobPipelineCreateRequest
from mawhub.app.job.repo.job_pipeline_repo import JobPipelineRepoInterface
from mawhub.app.job.repo.job_repo import JobRepoInterface
from mawhub.sqltypes.table_models import JobPipeline

class JobPipelineUsecaseInterface(Protocol):
	def job_pipeline_create_update(self, payload: JobPipelineCreateRequest)->Document: ...

class JobPipelineUsecase:
    repo: JobRepoInterface
    def __init__(
        self,
        repo: JobRepoInterface,
    ):
        self.repo = repo

    def job_pipeline_create_update(self, payload: JobPipelineCreateRequest)->Document:
        params = cast(JobPipeline , payload)
        return self.repo.job_pipeline.create_or_update(params)

