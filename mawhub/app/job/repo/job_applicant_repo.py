from typing import List, Protocol
import frappe

from mawhub.app.job.dto.job_applicant import  JobApplicantBulkUpdateRequest, JobApplicantUpdateRequest


class JobApplicantRepoInterface(Protocol):
	def job_applicant_update(self, payload: JobApplicantUpdateRequest)->str: ...
	def job_applicant_bulk_update(self, payload: JobApplicantBulkUpdateRequest)->List[str]: ...



class JobApplicantRepo:
    def job_applicant_update(self, payload: JobApplicantUpdateRequest)->str:
        doc = frappe.get_doc("Job Applicant",payload.get("name"))
        doc.set('status' , payload.get('status'))
        doc.set('custom_pipeline_step' , payload.get('pipeline_step'))
        doc.save(ignore_permissions=True)
        frappe.db.commit()
        return payload.get('name')


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
