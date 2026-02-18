from typing import  Protocol
from mawhub.app.job.dto.applicant_resume_dto import ApplicantResumeDTO
from mawhub.mawhub.doctype.applicant_resume.applicant_resume import ApplicantResumeDBModel
from mawhub.pkg.baseclasses.app_repo import AppRepo, AppRepoInterface


class ApplicantResumeRepoInterface(AppRepoInterface[ApplicantResumeDTO],Protocol):
    pass



class ApplicantResumeRepo(AppRepo[ApplicantResumeDBModel]):
    def __init__(self):
        super().__init__(
            doc_name="Applicant Resume",
            name_key="name",
            scalar_fields=[
                "name",

                "file_hash",
                "email",
                "phone",
                "location",
                "file_path",
                "links",
                "summary",
                "output",
                "skills",
            ],
            child_tables=[
                "experience",
                "education",
                "projects"
                ]
            ,
        )
