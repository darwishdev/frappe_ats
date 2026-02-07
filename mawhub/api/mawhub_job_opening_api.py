from typing import  List,  cast
import frappe
from mawhub.app.job.dto.job_opening import JobOpeningDTO
from mawhub.bootstrap import app_container
from typing import  List, cast
from frappe import  _
import frappe
from mawhub.bootstrap import app_container
from mawhub.sqltypes.table_models import JobOpening


@frappe.whitelist(methods=["GET" , "POST"], allow_guest=True)
def job_opening_list(
        customer:str,
        owner:str,
)->List[JobOpeningDTO]:
    return app_container.job_usecase.job_opening.job_opening_list({"customer" : customer,"owner" : owner})


@frappe.whitelist(methods=["GET" , "POST"], allow_guest=True)
def job_opening_find(job:str)->JobOpeningDTO:
    return app_container.job_usecase.job_opening.job_opening_find(job)

@frappe.whitelist(methods=["PUT" , "POST"], allow_guest=True)
def job_opening_create_update(payload:dict):
    return app_container.job_usecase.job_opening.job_opening_create_update(cast(JobOpening,payload))
@frappe.whitelist(methods=["POST"])
def generate_applicant_email(applicant: dict, job: dict, pipeline_step: str,user_instructions: str = "") -> str:
    """
    Generates a personalized email for a candidate based on JD and Resume.
    """
    try:
        agent = app_container.job_usecase.communication_agent

        email_response = agent.generate_candidate_email(
            job_info=job,
            applicant_info=applicant,
            pipeline_step=pipeline_step,
            user_instructions=user_instructions
        )

        # 4. Return as a dictionary for the frontend
        return str(email_response.model_dump())

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Email Generation Error")
        raise Exception(f"Error generating email: {str(e)}")
