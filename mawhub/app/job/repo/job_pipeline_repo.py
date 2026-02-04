from typing import  Protocol
from mawhub.pkg.baseclasses.app_repo import AppRepo, AppRepoInterface
from mawhub.sqltypes.table_models import JobPipeline

class JobPipelineRepoInterface(AppRepoInterface[JobPipeline],Protocol):
    pass

class JobPipelineRepo(AppRepo[JobPipeline]):
    def __init__(self):
        super().__init__(
            doc_name="Job Pipeline",
            name_key="name",
            scalar_fields=[
                "name",
                "description",
            ],
            child_tables={
                "steps": "steps",
            },
        )
