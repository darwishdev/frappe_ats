from typing import  Protocol
from mawhub.mawhub.doctype.job_pipeline.job_pipeline import JobPipelineDBModel
from mawhub.pkg.baseclasses.app_repo import AppRepo, AppRepoInterface
# from mawhub.sqltypes.table_models import JobPipeline

class JobPipelineRepoInterface(AppRepoInterface[JobPipelineDBModel],Protocol):
    pass

class JobPipelineRepo(AppRepo[JobPipelineDBModel]):
    def __init__(self):
        super().__init__(
            doc_name="Job Pipeline",
            name_key="name",
            scalar_fields=[
                "name",
                "is_primary",
                "description",
            ],
            child_tables={
                "steps": "steps",
            },
        )
