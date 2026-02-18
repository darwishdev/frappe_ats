import frappe
from mawhub.app.job.dto.job_pipeline_dto import JobPipelineCreateRequest
from mawhub.bootstrap import app_container
from frappe import _
import frappe
from mawhub.bootstrap import app_container
from mawhub.mawhub.doctype.job_pipeline.job_pipeline import JobPipelineDBModel


@frappe.whitelist(methods=["PUT" , "POST"], allow_guest=True)
def job_pipeline_create_update(payload:JobPipelineDBModel):
    return app_container.job_usecase.job_pipeline.job_pipeline_create_update(payload)
