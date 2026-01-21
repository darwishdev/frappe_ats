from frappe import _
from typing import List, Protocol, cast

from frappe.model.document import Document
from mawhub.app.job.agent.resume_parser_agent import ResumeWorkflow
from mawhub.app.job.dto.applicant_resume import ApplicantResumeDTO
from mawhub.app.job.repo.job_repo import JobRepoInterface
from mawhub.pkg.pdfconvertor.pdfconvertor import extract_text_from_pdf


class ApplicantResumeUsecaseInterface(Protocol):
	def applicant_resume_create_update(self, payload: ApplicantResumeDTO)->Document: ...
	def applicant_resume_parse(
        self,
        path:str
    )->ApplicantResumeDTO: ...
	def applicant_resume_bulk_create(
        self,
        payload:List[ApplicantResumeDTO]
    )->List[Document]: ...

class ApplicantResumeUsecase:
    repo: JobRepoInterface
    resume_agent: ResumeWorkflow
    def __init__(
        self,
        repo: JobRepoInterface,
        resume_agent: ResumeWorkflow
    ):
        self.repo = repo
        self.resume_agent = resume_agent

    def applicant_resume_create_update(self, payload: ApplicantResumeDTO)->Document:
        return self.repo.applicant_resume.applicant_resume_create_update(payload)

    def applicant_resume_parse(
        self,
        path:str
    )->ApplicantResumeDTO:
        txt = extract_text_from_pdf(path)
        parsed_resume = self.resume_agent.run(txt)
        return cast(ApplicantResumeDTO , parsed_resume)
    def applicant_resume_bulk_create(
        self,
        payload:List[ApplicantResumeDTO]
    )->List[Document]:
        return self.repo.applicant_resume.applicant_resume_bulk_create(payload)
