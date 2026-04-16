from typing import Protocol

from mawhub.mawhub.doctype.workable_event.workable_event import WorkableEventDBModel
from mawhub.pkg.baseclasses.app_repo import AppRepo, AppRepoInterface


class WorkableEventRepoInterface(AppRepoInterface[WorkableEventDBModel], Protocol):
    pass


class WorkableEventRepo(AppRepo[WorkableEventDBModel]):
    def __init__(self):
        super().__init__(
            doc_name="Workable Event",
            name_key="name",
            ignore_links=True,
            scalar_fields=[
                "name",
                "title",
                "event_type",
                "cancelled",
                "starts_at",
                "ends_at",
                "conference_type",
                "conference_url",
                "job",
                "job_title",
                "candidate",
                "candidate_name",
                "description",
                "members",
            ],
        )
