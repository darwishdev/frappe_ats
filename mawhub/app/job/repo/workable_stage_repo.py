from typing import Protocol

from mawhub.mawhub.doctype.workable_stage.workable_stage import WorkableStageDBModel
from mawhub.pkg.baseclasses.app_repo import AppRepo, AppRepoInterface


class WorkableStageRepoInterface(AppRepoInterface[WorkableStageDBModel], Protocol):
    pass


class WorkableStageRepo(AppRepo[WorkableStageDBModel]):
    def __init__(self):
        super().__init__(
            doc_name="Workable Stage",
            name_key="name",
            scalar_fields=[
                "name",
                "stage_name",
                "kind",
                "position",
            ],
        )
