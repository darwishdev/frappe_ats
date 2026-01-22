import json
from frappe import Any, _
from typing import Generator, List, Protocol, cast

import frappe
from frappe.model.document import Document
from frappe.utils import now
from mawhub.app.job.agent.resume_parser_agent import ResumeWorkflow
from mawhub.app.job.dto.applicant_resume import ApplicantResumeDTO
from mawhub.app.job.dto.job_applicant import JobApplicantCreateWithResume
from mawhub.app.job.repo.job_repo import JobRepoInterface
from mawhub.pkg.pdfconvertor.pdfconvertor import extract_text_from_pdf
from mawhub.sqltypes.table_models import JobApplicant


class ApplicantResumeUsecaseInterface(Protocol):
	def applicant_resume_create_update(self, payload: ApplicantResumeDTO)->Document: ...
	def job_applicant_create_with_resume(self, payload: JobApplicantCreateWithResume)->Document: ...
	def sse_generator(self, resume_text: str, job_opening_id: str, pipeline_step_id: str)->Generator[str, Any, None]: ...

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

    def job_applicant_create_with_resume(self, payload: JobApplicantCreateWithResume)->Document:
        applicant_resume = payload.get("applicant_resume")
        personal_info = applicant_resume.get("personal")
        if not personal_info:
            raise ValueError(f"personal is required {json.dumps(applicant_resume)}")
        create_update_params : JobApplicant = {
            "name": str(personal_info.get("email")),
            "email_id":str(personal_info.get("email")),
            "applicant_name": str(personal_info.get("name")),
            "custom_pipeline_step": payload.get("pipeline_step_id"),
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

    def sse_generator(self , resume_text: str , job_opening_id: str, pipeline_step_id: str):
        workflow = self.resume_agent
        try:
            if resume_text == "":
                raise ValueError("cant parse the resume text")
            final_result = None
            for update in workflow.run(resume_text):
                final_result = update  # Keep track of the latest state
                yield f"data: {json.dumps(update)}\n\n"
# 2. After the loop finishes, we have the 'final_result'
            if final_result:
                # Construct the payload for the creation method
                res = cast(ApplicantResumeDTO , final_result['data'])
                skills_list = res.get('skills')
                if isinstance(skills_list , list):
                    res['skills'] =  ','.join(skills_list)
                creation_payload : JobApplicantCreateWithResume = {
                    "job_opening_id": job_opening_id,
                    "pipeline_step_id": pipeline_step_id,
                    "applicant_resume": res
                }

                # 3. Enqueue the creation method in the background
                # frappe.call("mawhub.job_applicant_create_with_resume",creation_payload)
                frappe.enqueue(
                    method="mawhub.job_applicant_create_with_resume",
                    queue="short",
                    now=True,
                    payload=creation_payload
                )
                # self.job_applicant_create_with_resume(creation_payload)
                yield f"data: {json.dumps(res)}\n\n"
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
