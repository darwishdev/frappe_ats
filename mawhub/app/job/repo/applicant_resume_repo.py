from typing import  Protocol
from mawhub.app.job.dto.applicant_resume_dto import ApplicantResumeDTO
from mawhub.pkg.baseclasses.app_repo import AppRepo, AppRepoInterface


class ApplicantResumeRepoInterface(AppRepoInterface[ApplicantResumeDTO],Protocol):
    pass



class ApplicantResumeRepo(AppRepo[ApplicantResumeDTO]):
    def __init__(self):
        super().__init__(
            doc_name="Applicant Resume",
            name_key="resume_hash",
            scalar_fields=[
                "resume_hash",
                "skills",
                "request_id",
                "file_path",
                "links",
                "email",
                "phone",
                "location",
                "summary",
                "output",
            ],
            child_tables={
                "experience": "experience",
                "education": "education",
                "projects": "projects",
                "links": "links",
            },
        )
