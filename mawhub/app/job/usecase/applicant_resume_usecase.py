import json
from frappe import Any, Union, _
from typing import Generator, Iterator, List, Literal, Protocol, TypedDict, cast

import frappe
from frappe.model.document import Document
from frappe.utils import now
from pydantic import PaymentCardNumber
from mawhub.app.job.agent.resume_parser_agent import AgentEvent, ResumeWorkflow
from mawhub.app.job.dto.applicant_resume import ApplicantResumeDTO
from mawhub.app.job.dto.job_applicant import JobApplicantCreateWithResume
from mawhub.app.job.repo.job_repo import JobRepoInterface
from mawhub.pkg.pdfconvertor.pdfconvertor import extract_text_from_pdf
from mawhub.sqltypes.table_models import JobApplicant

class ApplicantResumeUsecaseInterface(Protocol):
	def applicant_resume_create_update(self, payload: ApplicantResumeDTO)->Document: ...
	def job_applicant_create_with_resume(self, payload: JobApplicantCreateWithResume)->Document: ...

	def applicant_resume_parse(
        self,
        path:str,
    )->Iterator[AgentEvent]:...
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

    def job_applicant_create_with_resume(self, payload: JobApplicantCreateWithResume)->Document:
        applicant_resume = payload.get("applicant_resume")
        personal_info = applicant_resume.get("personal")
        if not personal_info:
            raise ValueError(f"personal is required {json.dumps(applicant_resume)}")
        step_name = payload.get("pipeline_step_id")
        if step_name == 'all':
            step_name = 'SC'
        create_update_params : JobApplicant = {
            "name": str(personal_info.get("email")),
            "email_id":str(personal_info.get("email")),
            "applicant_name": str(personal_info.get("name")),
            "custom_pipeline_step": step_name,
            "job_title": payload.get("job_opening_id"),
            "lower_range": 0.0,
            "upper_range": 0.0
        }
        job_applicant_doc = self.repo.job_applicant.create_or_update(create_update_params)
        if not job_applicant_doc:
            raise ValueError("cant create job_applicant_doc")
        applicant_resume_dto :ApplicantResumeDTO = {
            "job_applicant" : str(job_applicant_doc.get("name")),
            **applicant_resume
        }
        self.repo.applicant_resume.create_or_update(applicant_resume_dto)
        return job_applicant_doc

    def _sse_events(
        self,
        resume_text: str,
    ) -> Iterator[AgentEvent]:
        if not resume_text.strip():
            raise ValueError("cant parse the resume text")
        final_resume: ApplicantResumeDTO | None = None
        for update in self.resume_agent.run(resume_text):
            yield update
            if isinstance(update, dict) and "data" in update:
                final_resume = cast(ApplicantResumeDTO, update["data"])

        if not final_resume:
            raise ValueError("resume parsing finished without final result")
        skills = final_resume.get("skills")
        if isinstance(skills, list):
            final_resume["skills"] = ",".join(skills)

        # final_payload: JobApplicantCreateWithResume = {
        #     "job_opening_id": job_opening_id,
        #     "pipeline_step_id": pipeline_step_id,
        #     "applicant_resume": final_resume,
        # }

        yield {
            "event": "final",
            "data": final_resume,
        }
    def applicant_resume_parse(
        self,
        path:str,
    )->Iterator[AgentEvent]:
        txt = extract_text_from_pdf(path)
        try:
            for event in self._sse_events(
                txt,
            ):
                yield event
        except Exception as e:
            error_event: AgentEvent = {
                "event": "error",
                "data":  str(e),
            }
            yield error_event

    def applicant_resume_bulk_create(
        self,
        payload:List[ApplicantResumeDTO]
    )->List[Document]:
        return self.repo.applicant_resume.bulk_create(payload)
