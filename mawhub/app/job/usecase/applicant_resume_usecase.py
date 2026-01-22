import json
from frappe import Any, _
from typing import Generator, List, Protocol, cast

from frappe.model.document import Document
from mawhub.app.job.agent.resume_parser_agent import ResumeWorkflow
from mawhub.app.job.dto.applicant_resume import ApplicantResumeDTO
from mawhub.app.job.repo.job_repo import JobRepoInterface
from mawhub.pkg.pdfconvertor.pdfconvertor import extract_text_from_pdf


class ApplicantResumeUsecaseInterface(Protocol):
	def applicant_resume_create_update(self, payload: ApplicantResumeDTO)->Document: ...
	def sse_generator(self, resume_text: str)->Generator[str, Any, None]: ...
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
        return self.repo.applicant_resume.create_or_update(payload)


    def sse_generator(self , resume_text: str):
        workflow = self.resume_agent
        try:
            if resume_text == "":
                raise ValueError("cant parse the resume text")
            for update in workflow.run(resume_text):
                yield f"data: {json.dumps(update)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'status': 'error', 'message': str(e)})}\n\n"
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
        return self.repo.applicant_resume.bulk_create(payload)
