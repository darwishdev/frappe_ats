import asyncio
import json
import re
from typing import Iterator, List, cast
import frappe
from frappe.core.doctype.user.user import reset_user_data
from werkzeug.wrappers import Response
from mawhub.api.mawhub_parsed_document_api import parsed_document_from_agent_to_dto
from mawhub.app.job.agent.document_parser_agent import ParsedDocumentSection
from mawhub.app.job.dto.job_opening import JobOpeningDTO
from mawhub.bootstrap import app_container
from mawhub.pkg.pdfconvertor.pdfconvertor import extract_text_from_pdf

import asyncio
import json
from typing import Iterator, List, cast
from frappe import _
import frappe
from mawhub.bootstrap import app_container
from werkzeug.wrappers import Response

from queue import Queue
def sse_event(event: str, data):
    import json
    return (
        f"event: {event}\n"
        f"data: {json.dumps(data)}\n\n"
    )

@frappe.whitelist(methods=["POST", "GET"])
def job_opening_parse(path: str):
    """
    SSE endpoint to parse a document into structured sections.
    Streams updates for each section and a final event.
    """
    document_text = extract_text_from_pdf(path)
    workflow = app_container.job_usecase.document_parser_agent  # your workflow instance

    def sse_stream() -> Iterator[str]:
        try:
            # Run the workflow
            job_id = "1"
            context = {"meta_data": {}}
            parsed_job = ""
            for event in workflow.run(document_text=document_text):
                # Handle final event specially
                event_type = event.get("event")
                event_data = event.get("data", {})

                if event_type == "final":
                    final_sections_dto = parsed_document_from_agent_to_dto(event.get("data"),{},path,"job_opening",str(job_id))
                    print("Final parsed sections:", final_sections_dto)
                    event['data']['job_opening_details'] = parsed_job
                    app_container.job_usecase.parsed_document.parsed_document_create_update(final_sections_dto)
                yield f"data: {json.dumps(event)}\n\n"
                # 1. Intercept the first 'update' that contains titles/metadata
                if event_type == "update" and "titles" in event_data:

                    context["meta_data"] = event_data.get("metadata", {})

                    # --- NEW: Trigger Job Opening Extraction ---
                    # This is the synchronous method we just built
                    ai_job_data = app_container.job_usecase.job_agent.run(
                        chunked_doc=context["meta_data"]
                    )
                    parsed_job = ai_job_data.model_dump()
                    new_event_data = {
                        "event" : "update",
                        "job_opening_details" : parsed_job
                    }
                    new_event = {"event" : "update" , "data" : new_event_data}
# --- DIRECT FRAPPE CREATION (Quick & Dirty) ---
                    designation_name = parsed_job.get("job_title")
                    if designation_name and not frappe.db.exists("Designation", designation_name):
                        new_desig = frappe.get_doc({
                            "doctype": "Designation",
                            "designation_name": designation_name
                        })
                        new_desig.insert(ignore_permissions=True)
                    new_job = frappe.get_doc({
                        "doctype": "Job Opening",
                        "job_title": parsed_job.get("job_title"),
                        "designation": parsed_job.get("job_title"), # Usually maps to title
                        "description": parsed_job.get("description"),
                        "lower_range": parsed_job.get("lower_range") or 0.0,
                        "custom_pipeline" : "Main",
                        "upper_range": parsed_job.get("upper_range") or 0.0,
                        "currency": parsed_job.get("currency") or "SAR",
                        "company": "Mawhub", # Hardcoded default for now
                        "status": "Open",
                        "planned_vacancies": 1,
                        "publish": 1
                    })
                    new_job.insert(ignore_permissions=True)
                    frappe.db.commit() # Mandatory for SSE because it's a separate transaction
                    job_id = new_job.name
                    yield f"data: {json.dumps(new_event)}\n\n"

                # Always yield SSE formatted string


        except Exception as e:
            # Catch any errors in the workflow
            error_event = {
                "event": "error",
                "data": str(e),
            }
            frappe.db.rollback()
            yield f"data: {json.dumps(error_event)}\n\n"

    # Build the SSE response
    response = Response(sse_stream(), mimetype="text/event-stream")
    response.headers.add("Cache-Control", "no-cache")
    response.headers.add("X-Accel-Buffering", "no")  # prevent Nginx buffering

    return response
@frappe.whitelist(allow_guest=True)
def job_opening_parses(path: str):
    """
    SSE endpoint to parse a document.
    This will stream updates for each section and the final result.
    """

    document_text = extract_text_from_pdf(path)
    workflow = app_container.job_usecase.document_parser_agent

    def event_stream():
        for event in workflow.run(document_text=document_text):
            try:
                # Ensure event["data"] is never None
                data = event.get("data") or {}
                yield sse_event(event.get("event", "update"), data)
            except Exception as e:
                # Fallback for any serialization or None issues
                yield sse_event("error", {"message": f"SSE stream error: {str(e)}"})

    # Frappe streaming response for SSE
    frappe.local.response["type"] = "download"
    frappe.local.response["filename"] = None  # no filename needed
    frappe.local.response["filecontent"] = event_stream()
    frappe.local.response["content_type"] = "text/event-stream"
    return frappe.local.response
# @frappe.whitelist(methods=["GET" , "POST"], allow_guest=True)
# async def job_opening_parse(path:str):
#     txt = extract_text_from_pdf(path)
#     try:
#         result = await get_final_parsed_document(app_container.job_usecase.document_parser_agent,
#                                                  txt)
#         return result
#         print("Final Parsed Document:", result)
#     except Exception as e:
#         print(f"Workflow failed: {e}")
#     def sse_stream() -> Iterator[str]:
#         try:
#             # Use the new typed usecase method
#             for event in app_container.job_usecase.job_opening.job_opening_parse(
#                 path,
#             ):
#                 yield f"data: {json.dumps(event)}\n\n"
#         except Exception as e:
#             error_event  = {
#                 "event": "error",
#                 "data": str(e),
#             }
#     #         yield f"data: {json.dumps(error_event)}\n\n"
    #
    # # 3️⃣ Return a proper SSE Response
    # response = Response(sse_stream(), mimetype="text/event-stream")
    #
    # # 4️⃣ Required headers for SSE to work properly
    # response.headers.add("Cache-Control", "no-cache")
    # response.headers.add("X-Accel-Buffering", "no")  # Crucial for Nginx buffering

@frappe.whitelist(methods=["GET" , "POST"], allow_guest=True)
def job_opening_list()->List[JobOpeningDTO]:
    return app_container.job_usecase.job_opening.job_opening_list("Administrator")


@frappe.whitelist(methods=["GET" , "POST"], allow_guest=True)
def job_opening_find(job:str)->JobOpeningDTO:
    return app_container.job_usecase.job_opening.job_opening_find(job)
