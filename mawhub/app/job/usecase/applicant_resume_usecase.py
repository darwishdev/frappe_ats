import hashlib
import json
from typing import  Iterator, List,  Protocol,  cast

import frappe
from frappe.model.document import Document
from mawhub.app.job.agent.resume_parser_agent import AgentFinalEvent,  ResumeWorkflow
from mawhub.app.job.dto.applicant_resume_dto import ApplicantResumeDTO
from mawhub.app.job.dto.job_applicant import JobApplicantCreateWithResume
from mawhub.app.job.repo.job_repo import JobRepoInterface
from mawhub.pkg.overrides import job_opening
from mawhub.pkg.overrides.job_opening import CustomJobOpening
from mawhub.pkg.pdfconvertor.pdfconvertor import  get_document_content_and_hash
from mawhub.pkg.sql.sql_utils import get_cached_output
from mawhub.sqltypes.table_models import JobApplicant
class ResumeParseError(Exception): ...
class ResumeAgentError(Exception): ...
class ResumePersistenceError(Exception): ...
class JobLinkError(Exception): ...
# Even simpler version - just map essential fields
def job_applicant_dto_from_agent(agent_final: AgentFinalEvent,path:str) -> JobApplicant:
    """Minimal conversion with only essential fields mapped."""
    personal = agent_final.get("personal", {})
    resp : JobApplicant = {
        "lower_range": 0.0,
        "upper_range": 0.0,
        "status": "Open",
        "resume_attachment":path,
        "applicant_rating": 0.0,
        "applicant_name": personal.get("name", ""),
        "email_id": personal.get("email", ""),
        "phone_number": personal.get("phone", ""),
        # "country": personal.get("location", ""),
    }
    return resp
def applicant_resume_dto_from_agent(
    final: AgentFinalEvent,
    resume_hash:str,
    request_id:str,
    file_path:str,
) -> ApplicantResumeDTO:
    personal = final["personal"]
    email = personal["email"]

    dto: ApplicantResumeDTO = {
        "job_applicant": email,
        "request_id": request_id,
        "raw_resume_text" : json.dumps(final , default=str),
        "file_path": file_path,
        "personal": personal,
        "resume_hash": resume_hash
    }

    # optional fields — add only if present & not empty

    if final.get("summary"):
        dto["summary"] = final["summary"]

    skills_list = final.get("skills")
    if skills_list:
        dto["skills"] = ", ".join(skills_list)

    if final.get("experience"):
        dto["experience"] = final["experience"]

    if final.get("education"):
        dto["education"] = final["education"]

    if final.get("projects"):
        dto["projects"] = final["projects"]

    return dto
class ApplicantResumeUsecaseInterface(Protocol):
	def applicant_resume_create_update(self, payload: ApplicantResumeDTO)->Document: ...
	def job_applicant_create_with_resume(self, payload: JobApplicantCreateWithResume)->Document: ...

	def applicant_resume_parse(
        self,
        path:str,
        job:str,
        step:str,
        request_id:str
    )->Iterator[str]:...
	def applicant_resume_bulk_create(
        self,
        payload:List[ApplicantResumeDTO]
    )->List[Document]: ...

class ApplicantResumeUsecase:
    repo: JobRepoInterface
    resume_agent: ResumeWorkflow
    doc_name : str
    def __init__(
        self,
        repo: JobRepoInterface,
        resume_agent: ResumeWorkflow
    ):
        self.repo = repo
        self.resume_agent = resume_agent
        self.doc_name = "Applicant Resume"
    def applicant_resume_bulk_create(
            self,
            payload:List[ApplicantResumeDTO]
            )->List[Document]:
        return self.repo.applicant_resume.bulk_create(payload)

    def applicant_resume_create_update(self, payload: ApplicantResumeDTO)->Document:
        return self.repo.applicant_resume.create_or_update(payload)


    def job_applicant_link_with_job_opening(
        self,
        job: str,
        email: str,
        step: str,
        resume_id: str,
    ) -> None:
        job_doc = frappe.get_doc("Job Opening", job)
        if not job_doc:
            raise frappe.ValidationError(f"job opening {job} is not found")

        # cast so type checker knows our custom methods exist
        job_doc = cast(CustomJobOpening, job_doc)
        try:
            job_doc.link_applicant_to_step(
                applicant_id=email,
                step_code=step,
                resume_id=resume_id,
                comment="Linked via job_applicant_link_with_job_opening"
            )

            job_doc.save()
            frappe.db.commit()
        except Exception:
            frappe.db.rollback()
            frappe.log_error(frappe.get_traceback(), "Job Applicant Linking Failed")
            raise JobLinkError(
                f"job={job} email={email} step={step} resume={resume_id}"
            )


    def get_text_hash(self, text: str) -> str:
        clean_text = text.strip().encode('utf-8')
        return hashlib.sha256(clean_text).hexdigest()

    def applicant_resume_parse(
        self,
        path:str,
        job:str,
        step:str,
        request_id:str
    )->Iterator[str]:
        try:
            document_text, document_text_hash = get_document_content_and_hash(path)
        except Exception:
            frappe.log_error(frappe.get_traceback(), "PDF Read Failed")
            raise ResumeParseError("Failed to read document")
        def callback(name:str , event_data: AgentFinalEvent):
            try:
                job_applicant_params = job_applicant_dto_from_agent(event_data , path)
                self.repo.job_applicant.create_or_update(job_applicant_params)
                self.job_applicant_link_with_job_opening(
                    job=job,
                    email=event_data["personal"]["email"],
                    step=step,
                    resume_id=name,
                )
            except Exception:
                frappe.log_error(frappe.get_traceback(), "Callback Failed")
                raise ResumePersistenceError("Applicant creation/link failed")

        final_event : AgentFinalEvent | None = None
        cached = None
        try:
            cached = get_cached_output(
                doctype="Applicant Resume",
                output_field="raw_resume_text",
                key_value=document_text_hash,
                key_field="resume_hash",
                expected_type=AgentFinalEvent
            )
        except Exception:
            frappe.log_error(frappe.get_traceback(), "Resume Cache Read Failed")
        if cached:
            name , cached_resume = cached
            callback(name , cached_resume)
            return
        try:
            for event in self.resume_agent.run(document_text):
                if event["event"] == "final":
                    final_event = event["data"]
                json_data = json.dumps(event , default=str)
                yield f"data: {json_data}\n\n"
        except Exception:
            frappe.log_error(frappe.get_traceback(), "Resume Agent Failed")
            raise ResumeAgentError("AI agent failed")

        if not final_event:
            return
        try:
            res_dto = applicant_resume_dto_from_agent(
                    final_event,
                    document_text_hash,
                    request_id,
                    path)
            resume_doc = self.applicant_resume_create_update(res_dto)
            callback(str(resume_doc.name) , final_event)
        except Exception as e:
            frappe.log_error(frappe.get_traceback(), "Resume Agent Failed")
            frappe.db.rollback()
            frappe.log_error(
                frappe.get_traceback(),
                "Applicant Resume Save Failed"
            )
            raise ResumePersistenceError(
                f"resume_save_failed request_id={request_id}"
            ) from e
