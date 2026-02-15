from typing import List, Protocol
import frappe

from mawhub.app.job.dto.job_applicant_dto import  JobApplicantBulkUpdateRequest
from mawhub.pkg.baseclasses.app_repo import AppRepo, AppRepoInterface
from mawhub.sqltypes.table_models import JobApplicant


class JobApplicantRepoInterface(AppRepoInterface[JobApplicant] , Protocol):
    def job_applicant_bulk_update(self, payload: JobApplicantBulkUpdateRequest)->List[str]: ...
    def job_applicant_find(self, name: str,job: str)->dict: ...


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



    def job_applicant_find(self, name: str,job: str)->dict:
        applicant_doc = frappe.get_doc("Job Applicant" , name)
        interviews = frappe.get_all(
                "Interview" ,
                filters={"job_applicant" : name} ,
                fields=[
                    "name",
                    "creation",
                    "modified",
                    "modified_by",
                    "owner",
                    "docstatus",
                    "interview_round",
                    "job_applicant",
                    "job_opening",
                    "designation",
                    "resume_link",
                    "status",
                    "scheduled_on",
                    "from_time",
                    "to_time",
                    "expected_average_rating",
                    "average_rating",
                    "interview_summary",
                    "reminded",
                    "amended_from"
                    ]
                )
        response = {
                "applicant" : applicant_doc.as_dict(),
                "interviews" : interviews,
                }

        applicant_resume = frappe.db.sql("""
                                select a.applicant_resume from `tabJob Opening Applicant` a
                                where a.parent = %(job)s
                                AND a.parenttype = 'Job Opening'
                                AND a.job_applicant = %(applicant)s
                                AND a.invalidated_at IS NULL
                                LIMIT 1
                                """ , {"job" : job , "applicant" : name} , pluck=True)
        if not applicant_resume:
            print(f"""can't find the active resume for this candidate : {name} on this
                                         job : {job}""")
            return response
        if not isinstance(applicant_resume , list):
            return response
        if len(applicant_resume) == 0:
            return response
        applicant_resume = applicant_resume[0]
        resume_doc = frappe.get_doc("Applicant Resume" , str(applicant_resume))
        return {
            "applicant" : applicant_doc.as_dict(),
            "resume" : resume_doc.as_dict(),
            "interviews" : interviews,
        }

        return response
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
