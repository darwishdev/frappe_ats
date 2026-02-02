from typing import Iterator
from werkzeug.wrappers import Response
from mawhub.bootstrap import app_container
from frappe import _
import frappe
from mawhub.app.job.dto.parsed_document_dto import ParsedDocumentDTO, ParsedDocumentParseRequest
from mawhub.pkg.pdfconvertor.pdfconvertor import extract_text_from_pdf
from mawhub.pkg.realtime.sse_utils import sse_event
import json
import frappe
from werkzeug.wrappers import Response

from mawhub.sqltypes.table_models import JobOpening

@frappe.whitelist(methods=["PUT" , "POST"], allow_guest=True)
def parsed_document_create_update(payload:ParsedDocumentDTO):
    return app_container.job_usecase.parsed_document.parsed_document_create_update(payload)

@frappe.whitelist(methods=["POST", "GET"], allow_guest=True)
def parsed_document_parse(payload: ParsedDocumentParseRequest):
    def final_event_callback(final_event: dict):
        try:
            # Initialize the LLM agent

            # Run the agent to get JobOpeningSchema
            job_event = app_container.job_usecase.job_agent.run(final_event)
            job_opening_create_params : JobOpening = {
                "name": "",  # required for new doc
                "job_title": job_event["job_title"] or "Untitled",
                "designation": job_event.get("designation") or "",
                "custom_customer": job_event.get("customer") or "",
                "location": job_event.get("location") or "",
                "planned_vacancies": job_event.get("planned_vacancies", 1),
                "vacancies": job_event.get("vacancies", 1),
                "lower_range": job_event.get("lower_range", 0.0),
                "upper_range": job_event.get("upper_range", 0.0),
                "publish": job_event.get("publish", 1),
                "publish_salary_range": job_event.get("publish_salary_range", 1),
                "publish_applications_received": job_event.get("publish_applications_received", 1),
            }
            job_create_req = app_container.job_usecase.job_opening.job_opening_create_update(job_opening_create_params)
            print(f"final event is hapening here")
            print(f"final event is hapening here")
            print(f"final event is hapening here {job_create_req}")
            print(f"final event is hapening here")
            print(f"final event is hapening here")

            # Convert schema to TypedDict event
            # job_event = job_opening_schema_to_event(job_schema)

            # Call the actual API to create/update job opening
            # app_container.job_usecase.job_opening_create_update(job_event)

        except Exception as e:
            # Optionally log the error
            frappe.log_error(f"JobOpening creation failed: {str(e)}", "parsed_document_parse")
    response = Response(app_container.job_usecase.parsed_document.parse_document(payload,on_final_event=final_event_callback), mimetype="text/event-stream")
    response.headers.update({
        "Cache-Control": "no-cache",
        "X-Accel-Buffering": "no",  # Disables Nginx buffering for instant delivery
        "Connection": "keep-alive"
    })

    return response
