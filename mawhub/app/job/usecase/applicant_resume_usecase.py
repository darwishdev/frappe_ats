import hashlib
import json
from frappe import Any, Callable, Optional, Union, _
from typing import Dict, Generator, Iterator, List, Literal, Protocol, TypedDict, cast

import frappe
from frappe.model.document import Document
from frappe.utils import now
from pydantic import BaseModel
from mawhub.app.job.agent import resume_parser_agent
from mawhub.app.job.agent.resume_parser_agent import ResumeParserEvent, ResumeWorkflow
from mawhub.app.job.dto import applicant_resume_dto
from mawhub.app.job.dto.applicant_resume_dto import ApplicantResumeDTO
from mawhub.app.job.dto.job_applicant import JobApplicantCreateWithResume
from mawhub.app.job.repo.job_repo import JobRepoInterface
from mawhub.pkg.overrides.job_opening import CustomJobOpening
from mawhub.pkg.pdfconvertor.pdfconvertor import extract_text_from_pdf, get_document_content_and_hash
from mawhub.sqltypes.table_models import JobApplicant

class ApplicantResumeUsecaseInterface(Protocol):
	def applicant_resume_create_update(self, payload: ApplicantResumeDTO)->Document: ...
	def job_applicant_create_with_resume(self, payload: JobApplicantCreateWithResume)->Document: ...

	def applicant_resume_parse(
        self,
        path:str,
        job:str,
        step:str,
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


    def _transform_section_to_dto(
        self,
        event: resume_parser_agent.AgentSectionEvent
    ) -> dict :
        """
        Maps a single AI section result to its DTO-compatible dictionary/list format.
        """
        final_event = {}
        section_name = event["name"]
        content = event["content"]
        if not content:
            return final_event

        # Handle Personal Info
        if section_name == "personal" and isinstance(content, resume_parser_agent.PersonalInfo):
            final_event[event["name"]] = {
                "name": content.name,
                "email": content.email,
                "phone": content.phone,
                "location": content.location,
                "links": content.links
            }
            return final_event

        # Handle Skills (Converting List[str] to comma-separated string)
        if section_name == "skills" and isinstance(content, resume_parser_agent.SkillList):
            final_event["skills"] = ", ".join(content.items)
            return final_event
        # if section_name == "summary" and isinstance(content, str):
        #     final_event["summary"] = content
        #     return final_event
        #
        # Handle Lists (Experience, Education, Projects)
        if hasattr(content, "items") and isinstance(content , BaseModel):
            items = getattr(content,"items")
            final_event[event["name"]] = [item.model_dump() for item in items ]
            return final_event

        # if isinstance(content , str):
        #     final_event[event["name"]] = content
        # Handle Summary (Raw string)
        return final_event
    def applicant_resume_bulk_create(
            self,
            payload:List[ApplicantResumeDTO]
            )->List[Document]:
        return self.repo.applicant_resume.bulk_create(payload)

    def applicant_resume_create_update(self, payload: ApplicantResumeDTO)->Document:
        return self.repo.applicant_resume.create_or_update(payload)

    # def job_applicant_create_with_resume(self, payload: JobApplicantCreateWithResume)->Document:
    #     applicant_resume = payload.get("applicant_resume")
    #     personal_info = applicant_resume.get("personal")
    #     if not personal_info:
    #         raise ValueError(f"personal is required {json.dumps(applicant_resume)}")
    #     step_name = payload.get("pipeline_step_id")
    #     if not step_name or step_name == "null":
    #         step_names = frappe.db.sql("""
    #             SELECT name FROM `tabPipeline Step` s
    #             WHERE s.parent = %s
    #             ORDER BY idx ASC
    #             LIMIT 1
    #                              """ , (payload.get('job_opening_id'),),pluck=True ) or []
    #         typed_names = cast(List[str] , step_names)
    #         if len(typed_names) == 0:
    #             raise frappe.ValidationError("Please set valid pipeline steps to the job opening")
    #         step_name = typed_names[0]
    #
    #     email = personal_info.get("email" ,"")
    #     # if frappe.db.exists("Job Applicant" , email):
    #     create_update_params : JobApplicant = {
    #         "name": email,
    #         "email_id":email,
    #         "applicant_name": str(personal_info.get("name")),
    #         "custom_pipeline_step": step_name,
    #         "job_title": payload.get("job_opening_id"),
    #         "lower_range": 0.0,
    #         "upper_range": 0.0
    #     }
    #     job_applicant_doc = self.repo.job_applicant.create_or_update(create_update_params)
    #     if not job_applicant_doc:
    #         raise ValueError("can't create job_applicant_doc")
    #     applicant_resume_dto :ApplicantResumeDTO = {
    #         "job_applicant" : str(job_applicant_doc.get("name")),
    #         **applicant_resume
    #     }
    #     self.repo.applicant_resume.create_or_update(applicant_resume_dto)
    #     return job_applicant_doc



    # def applicant_create_from_resume(
    #     self,
    #     parsed_resume: ApplicantResumeDTO
    # ):
    #     personal = parsed_resume["personal"]
    #     email = personal["email"]
    #     is_candidate_stored = frappe.db.exists("Job Applicant" , email)
    #     if not is_candidate_stored:
    #         job_applicant_params : JobApplicant  = {
    #                 "name" : email,
    #                 "email_id":email,
    #                 "phone_number":personal.get("phone",""),
    #                 "lower_range":1.0,
    #                 "upper_range":1.0,
    #                 }
    #
    #         try:
    #             created_applicant =  self.repo.job_applicant.create_or_update(job_applicant_params)
    #             print("applcant created")
    #             print(created_applicant)
    #             return created_applicant
    #         except Exception as e:
    #             raise Exception(f"failed_to_insert_cadndiate : params : {job_applicant_params} error : {str(e)}")

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
            new_row = job_doc.link_applicant_to_step(
                applicant_id=email,
                step_code=step,
                resume_id=resume_id,
                comment="Linked via job_applicant_link_with_job_opening"
            )

            job_doc.save()
            frappe.db.commit()

            print(
                f"linked applicant={email} "
                f"step={new_row.get('step')} "
                f"job={job}"
            )

        except Exception as e:
            raise Exception(
                "failed_to_link_job_with_applicant : "
                f"params : {json.dumps({'email': email, 'step': step, 'resume': resume_id})} : "
                f"{str(e)}"
            )


    def get_text_hash(self, text: str) -> str:
        clean_text = text.strip().encode('utf-8')
        return hashlib.sha256(clean_text).hexdigest()

    def applicant_resume_parse(
        self,
        path:str,
        job:str,
        step:str,
    )->Iterator[str]:
        job_doc = frappe.get_doc("Job Opening" , job)
        if not job_doc:
            raise frappe.ValidationError(f"job opening {job} is not found")
        job_candidates = job_doc.get("custom_candidates")
        if not job_candidates:
            job_doc.set("custom_candidates" , [])
        document_text , document_text_hash= get_document_content_and_hash(path)
        # cache_params = {"resume_hash" : document_text_hash}
        # cached_resume_doc = frappe.get_last_doc(
        #             doc_name,
        #             filters=cache_params
        #             )
        # if cached_resume_doc:
            # cached_resume_doc_txt = cached_resume_doc.get("raw_resume_text")
            # if isinstance(cached_resume_doc_txt,str):
            #     cached_resume_doc_parsed = json.loads(str(cached_resume_doc_txt))
            #     json_data = json.dumps({"event" : "final" ,"data" : cached_resume_doc_parsed} , default=str)
            #     yield f"data: {json_data}\n\n"
            #     doc_name = cached_resume_doc.name
            #     job_applicant_id = cached_resume_doc.get("job_applicant")
            #     self.job_applicant_link_with_job_opening(job,str(job_applicant_id),str(step),str(doc_name))
        final_event_data: dict = {}
        for event in self.resume_agent.run(document_text):
            if event["event"] == "update":
                event_data = event["data"]
                converted_event_data = self._transform_section_to_dto(event_data)
                final_event_data = {
                        **final_event_data,
                        **converted_event_data
                }
                json_data = json.dumps({"event" : "update" ,"data" : converted_event_data} , default=str)
                yield f"data: {json_data}\n\n"

        final_data = {"event" : "final" , "data" : final_event_data}
        final_json_data = json.dumps(final_data , default=str)
        yield f"data: {final_json_data}\n\n"
        personal = final_event_data["personal"]
        email = personal["email"]
        final_event_dto = cast(ApplicantResumeDTO , final_event_data)
        print("doc has is")
        print("doc has is")
        print("doc has is")
        print("doc has is")
        print(document_text_hash)
        final_event_dto["resume_hash"] = document_text_hash
        final_event_dto["raw_resume_text"] = json.dumps(final_event_data)
        self.applicant_create_from_resume(final_event_dto)
        final_event_dto["job_applicant"] = email
        try:
            created_applicant_resume = self.applicant_resume_create_update(final_event_dto)
        except Exception as e:
            raise Exception(f"failed_to_insert_resume : params : {json.dumps(final_event_dto)} : {str(e)}")
        self.job_applicant_link_with_job_opening(job,email,step,str(created_applicant_resume.name))
