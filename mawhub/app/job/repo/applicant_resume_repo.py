from typing import List, Protocol, cast
import frappe

from mawhub.app.job.dto.applicant_resume import ApplicantResumeDTO
from frappe.model.document import Document

from mawhub.pkg.sql.crud_utils import bulk_create_docs, create_or_update_doc


class ApplicantResumeRepoInterface(Protocol):
    def applicant_resume_create_update(
        self,
        payload:ApplicantResumeDTO
    )->Document:...
    def applicant_resume_bulk_create(
        self,
        payloads: List[ApplicantResumeDTO]
    ) -> List[Document]:...



class ApplicantResumeRepo:
    doc_name : str
    name_key: str
    scalar_fields : List[str]
    child_tables : dict[str,str]
    def __init__(
        self,
    ):
        self.doc_name = 'Applicant Resume'
        self.name_key = 'job_applicant'
        self.scalar_fields = [
            "skills",
            "summary",
            "raw_resume_text",
            "raw_resume_json",
        ]
        self.child_tables = {
                "experience": "experience",
                "education": "education",
                "projects": "projects",
                "links": "links",
            }
    def applicant_resume_bulk_create(
        self,
        payloads: List[ApplicantResumeDTO]
    ) -> List[Document]:
        return bulk_create_docs(
            doctype=self.doc_name,
            items=cast(List[dict],payloads),
            name_key=self.name_key,
            scalar_fields=self.scalar_fields,
            child_tables=self.child_tables,
        )
    def applicant_resume_create_update(
            self,
            payload:ApplicantResumeDTO
    )->Document:
        job_applicant = payload.get("job_applicant")
        if not isinstance(job_applicant, str):
            raise frappe.ValidationError("job_applicant_required")
        return create_or_update_doc(
            doctype=self.doc_name,
            name=str(payload.get(self.name_key)),
            name_key=self.name_key,
            payload=cast(dict,payload),
            scalar_fields=self.scalar_fields,
            child_tables=self.child_tables,
        )
