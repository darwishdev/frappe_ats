import frappe
from mawhub.app.job.dto.job_pipeline_dto import JobPipelineCreateRequest
from mawhub.bootstrap import app_container
from frappe import _
import frappe
from mawhub.bootstrap import app_container


@frappe.whitelist(methods=["PUT" , "POST"], allow_guest=True)
def job_pipeline_create_update(payload:JobPipelineCreateRequest):
    return app_container.job_usecase.job_pipeline.job_pipeline_create_update(payload)
