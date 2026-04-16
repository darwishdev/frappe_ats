from typing import Protocol

from mawhub.mawhub.doctype.workable_candidate.workable_candidate import WorkableCandidateDBModel
from mawhub.pkg.baseclasses.app_repo import AppRepo, AppRepoInterface


class WorkableCandidateRepoInterface(AppRepoInterface[WorkableCandidateDBModel], Protocol):
    pass


class WorkableCandidateRepo(AppRepo[WorkableCandidateDBModel]):
    def __init__(self):
        super().__init__(
            doc_name="Workable Candidate",
            name_key="name",
            scalar_fields=[
                "name",
                # identity
                "firstname",
                "lastname",
                "email",
                "phone",
                # profile
                "headline",
                "address",
                "country",
                "country_code",
                "city",
                "region",
                # pipeline status
                "stage",
                "stage_kind",
                "disqualified",
                "disqualified_at",
                "disqualification_reason",
                "withdrew",
                # outcome
                "hired_at",
                "moved_to_offer_at",
                "sourced",
                "domain",
                "outlet",
                "common_source",
                "common_source_category",
                # links
                "profile_url",
                "resume_url",
                "resume_filename",
                "linkedin_url",
                # text
                "cover_letter",
                "summary",
                # json blobs
                "education_entries",
                "experience_entries",
                "skills",
                # sync metadata
                "workable_created_at",
                "workable_updated_at",
            ],
        )
