from typing import  Protocol
from mawhub.app.job.dto.applicant_resume import ApplicantResumeDTO
from mawhub.pkg.baseclasses.app_repo import AppRepo, AppRepoInterface


class ApplicantResumeRepoInterface(AppRepoInterface[ApplicantResumeDTO],Protocol):
    pass



class ApplicantResumeRepo(AppRepo[ApplicantResumeDTO]):
    def __init__(self):
        super().__init__(
            doc_name="Applicant Resume",
            name_key="job_applicant",
            scalar_fields=[
                "skills",
                "summary",
                "raw_resume_text",
                "raw_resume_json",
            ],
            child_tables={
                "experience": "experience",
                "education": "education",
                "projects": "projects",
                "links": "links",
            },
        )
