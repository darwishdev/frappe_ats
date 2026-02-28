from typing import   Any, List, Optional,  Protocol,  cast
import frappe
from frappe.model.document import Document
from mawhub.app.applicant.repo.applicant_repo import ApplicantRepoInterface
from mawhub.agent.file_text_parser.file_text_parser_agent import FileTextParserWorkflow
from mawhub.agent.resume_parser.resume_parser_agent import ResumeWorkflow
from mawhub.app.applicant.dto.applicant_resume_dto import ApplicantResumeDTO
from mawhub.app.applicant.dto.job_applicant_dto import job_applicant_dto_from_resume
from mawhub.mawhub.doctype.applicant_resume.applicant_resume import ApplicantResumeDBModel
from mawhub.pkg.overrides.job_opening import CustomJobOpening
from mawhub.pkg.pdfconvertor.pdfconvertor import  get_document_content_and_hash, get_text_hash
from mawhub.pkg.sql.sql_utils import ensure_designation, get_cached_output
class DocumentTextParserError(Exception): ...
class ApplicantResumeCreationError(Exception): ...
class ApplicantCreationError(Exception): ...
class ResumeCreationError(Exception): ...
class AgentGenerationError(Exception): ...

# Even simpler version - just map essential fields
class ApplicantResumeUsecaseInterface(Protocol):
	def applicant_resume_create_update(self, payload: ApplicantResumeDBModel)->Document: ...
	def applicant_resume_parse(
        self,
        path:str,
        job:str,
        user:str,
        step:str
    )->Any:...
	def applicant_resume_bulk_create(
        self,
        payload:List[ApplicantResumeDBModel]
    )->List[Document]: ...

class ApplicantResumeUsecase:
    repo: ApplicantRepoInterface
    resume_agent: ResumeWorkflow
    file_text_parser_agent: FileTextParserWorkflow
    doc_name : str
    def __init__(
        self,
        repo: ApplicantRepoInterface,
        resume_agent: ResumeWorkflow,
        file_text_parser_agent: FileTextParserWorkflow,
    ):
        self.repo = repo
        self.resume_agent = resume_agent
        self.file_text_parser_agent = file_text_parser_agent
        self.doc_name = "Applicant Resume"
    def applicant_resume_bulk_create(
            self,
            payload:List[ApplicantResumeDTO]
            )->List[Document]:
        return self.repo.applicant_resume.bulk_create(payload)

    def applicant_resume_create_update(
            self,
            payload: ApplicantResumeDTO ,
            file_path : Optional[str] = None,
            file_hash : Optional[str] = None
        )->Document:
        if file_path:
            payload["file_path"] = file_path

        if file_hash:
            payload["file_hash"] = file_hash
        return self.repo.applicant_resume.create_or_update(payload)


    def new_error_event(self,err:str,step:Optional[str]):
        event =  {
                "event" : "error",
                "data" : f"{err}"
                }
        if step:
            event["data"] += f" -- while executing {step}"
        return event
    def job_find(self,name :str) -> CustomJobOpening:
        job_doc = frappe.get_doc("Job Opening", name)
        if not job_doc:
            raise frappe.ValidationError(f"job opening {name} is not found")
        job_doc = cast(CustomJobOpening, job_doc)
        return job_doc
    def applicant_resume_parse(
        self,
        path:str,
        job:str,
        user:str,
        step:str,
    )->Any:
        def _publish(value:Any):
                frappe.publish_realtime(
                    event=f"resume_parser_progress:{job}",
                    message=value,
                    user=user
                )


        try:
            job_doc = self.job_find(job)
            document_text, document_text_hash = get_document_content_and_hash(path)
            if not document_text_hash:
                document_text = self.file_text_parser_agent.run(path)
                if not document_text:
                    raise DocumentTextParserError(f"failed to extract text from file : {path}")
                document_text_hash = get_text_hash(document_text)
            def link_with_job_opening(
                email: str,
                resume_id: str,
            ) -> None:
                print("link call counter issss"  )
                job_doc.link_applicant_to_step(
                    applicant_id=email,
                    step_code=step,
                    resume_id=resume_id,
                    comment="AI Parser"
                )
                _publish({"event" :"link_with_job" , "data" : {"applicant" : email , "resume" :
                                                               resume_id}})
            def create_applicant(event_data: ApplicantResumeDTO)->Document:
                try:
                    job_applicant_params = job_applicant_dto_from_resume(event_data , path)
                    designation = job_applicant_params.get("designation")
                    if designation:
                        designation_name = ensure_designation(designation)
                        job_applicant_params["designation"] = designation_name
                    applicant_doc = self.repo.job_applicant.create_or_update(job_applicant_params)
                    _publish({"event" :"applicant_creation" , "data" : {"name" : applicant_doc.name}})
                    return applicant_doc
                except Exception as e:
                    raise ApplicantCreationError(e)


            cache_name , cache_value = get_cached_output(
                doctype="Applicant Resume",
                key_value=document_text_hash,
                key_field="file_hash",
                expected_type=ApplicantResumeDTO
            )
            if cache_name and cache_value:
                email = str(cache_value.get("email"))
                _publish({"event" :"final" , "data" : cache_value})
                applicant_doc = create_applicant(cache_value)
                link_with_job_opening(email,cache_name)
                return

            if not cache_name:
                final_event : ApplicantResumeDTO | None = None
                for event in self.resume_agent.run(document_text):
                    _publish(event)
                    if event["event"] == "final":
                        final_event = event["data"]

                if not final_event:
                    raise AgentGenerationError(f"agent never returned final event")


                try:
                    resume_doc = self.applicant_resume_create_update(final_event , file_path=path ,file_hash=document_text_hash)

                except Exception as e:
                    raise ApplicantResumeCreationError(f"applicant_resume_creation: {str(e)}")
                _publish({"event" : "resume_creation" , "data" : {"name" : resume_doc.name}})
                applicant_doc = create_applicant(final_event)
                applicant_resume_name = str(resume_doc.name)
                email = str(applicant_doc.name)
                link_with_job_opening(email,applicant_resume_name)

        except Exception as e:
            _publish(self.new_error_event(str(e) , None))
            raise e


