from typing import List, Protocol
import frappe

from mawhub.app.job.dto.job_applicant import  JobApplicantBulkUpdateRequest
from mawhub.pkg.baseclasses.app_repo import AppRepo, AppRepoInterface
from mawhub.sqltypes.table_models import JobApplicant


class JobApplicantRepoInterface(AppRepoInterface[JobApplicant] , Protocol):
    def job_applicant_bulk_update(self, payload: JobApplicantBulkUpdateRequest)->List[str]: ...
    def job_applicant_find(self, name: str)->dict: ...


class JobApplicantRepo(AppRepo[JobApplicant]):
    def __init__(self):
        super().__init__(
            doc_name="Job Applicant",
            name_key="name",
            scalar_fields=[
                "applicant_name",
                "email_id",
                "phone_number",
                "country",
                "job_title",
                "designation",
                "status",
                "source",
                "source_name",
                "employee_referral",
                "applicant_rating",
                "notes",
                "cover_letter",
                "resume_attachment",
                "resume_link",
                "currency",
                "lower_range",
                "upper_range",
                "custom_pipeline_step",
            ],
            child_tables={
            },
        )
    # def job_applicant_update(self, payload: JobApplicantUpdateRequest)->str:
    #     doc = frappe.get_doc("Job Applicant",payload.get("name"))
    #     doc.set('status' , payload.get('status'))
    #     doc.set('custom_pipeline_step' , payload.get('pipeline_step'))
    #     doc.save(ignore_permissions=True)
    #     frappe.db.commit()
    #     return payload.get('name')



    def job_applicant_find(self, name: str)->dict:
        applicant_doc = frappe.get_doc("Job Applicant" , name)
        resume_doc = frappe.get_doc("Applicant Resume" , name)
        return {
            "applicant" : applicant_doc.as_dict(),
            "resume" : resume_doc.as_dict(),
        }
    def job_applicant_bulk_update(self, payload: JobApplicantBulkUpdateRequest)->List[str]:
        sql_stmt = """
        UPDATE `tabJob Applicant` a
        set
        a.status = %(status)s ,
        a.custom_pipeline_step = %(pipeline_step)s
        where a.name in  %(names)s
        """
        params = {
            "status": payload["status"],
            "pipeline_step": payload["pipeline_step"],
            "names": tuple(payload["names"]),  # IMPORTANT
        }
        try:
            frappe.db.sql(sql_stmt,params)
            frappe.db.commit()
        except Exception as e:
            frappe.db.rollback()
            raise e
        return payload.get('names')
