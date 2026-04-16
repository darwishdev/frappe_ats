from typing import Protocol

from mawhub.mawhub.doctype.workable_job.workable_job import WorkableJobDBModel
from mawhub.pkg.baseclasses.app_repo import AppRepo, AppRepoInterface


class WorkableJobRepoInterface(AppRepoInterface[WorkableJobDBModel], Protocol):
    pass


class WorkableJobRepo(AppRepo[WorkableJobDBModel]):
    def __init__(self):
        super().__init__(
            doc_name="Workable Job",
            name_key="name",
            scalar_fields=[
                "name",
                # header
                "workable_id",
                "title",
                "state",
                "confidential",
                # job details
                "full_title",
                "code",
                "department",
                "workplace_type",
                # classification
                "employment_type",
                "industry",
                "job_function",
                "experience",
                "education",
                # location
                "country",
                "country_code",
                "city",
                "region",
                "salary_currency",
                # urls
                "url",
                "application_url",
                "shortlink",
                "keywords",
                # rich text
                "description",
                "full_description",
                "requirements",
                "benefits",
                # sync metadata
                "workable_created_at",
                "workable_updated_at",
            ],
            child_tables={
                "stages": "stages",
                "candidates": "candidates",
            },
        )
