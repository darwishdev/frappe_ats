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
            for event in workflow.run(document_text=document_text):
                # Handle final event specially
                event_type = event.get("event")
                event_data = event.get("data", {})

                yield f"data: {json.dumps(event)}\n\n"
                # 1. Intercept the first 'update' that contains titles/metadata
                if event_type == "update" and "titles" in event_data:

                    context["meta_data"] = event_data.get("metadata", {})

                    # --- NEW: Trigger Job Opening Extraction ---
                    # This is the synchronous method we just built
                    ai_job_data = app_container.job_usecase.job_agent.run(
                        chunked_doc=context["meta_data"]
                    )
                    ai_txt = ai_job_data.model_dump()
                    new_event_data = {
                        "event" : "update",
                        "job_opening_details" : ai_txt
                    }
                    new_event = {"event" : "update" , "data" : new_event_data}
                    yield f"data: {json.dumps(new_event)}\n\n"
                    # Hydrate with defaults (adapter step)
                    # job_payload = adapter_to_full_job_opening(ai_job_data)

                    # Create the Job Opening record in Frappe
                    # new_job = app_container.job_usecase.job_opening.create(job_payload)
                    # job_id = new_job.name # Capture the actual Frappe ID

                    # Add the job info to the current event so the UI knows the Job ID
                    # event_data["job_opening_id"] = job_id
                    # event_data["job_details"] = job_payload
                if event_type == "final":
                    # The final data is a list of ParsedDocumentSection

                    final_sections_dto = parsed_document_from_agent_to_dto(event.get("data"),{},path,"job_opening" , "1")
                    # Optionally: do something with the final_sections (e.g., store in DB)
                    print("Final parsed sections:", final_sections_dto)
                    app_container.job_usecase.parsed_document.parsed_document_create_update(final_sections_dto)

                # Always yield SSE formatted string


        except Exception as e:
            # Catch any errors in the workflow
            error_event = {
                "event": "error",
                "data": str(e),
            }
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
