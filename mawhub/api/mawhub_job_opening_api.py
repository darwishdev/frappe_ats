import asyncio
import json
from typing import Iterator, List, cast
import frappe
from frappe.core.doctype.user.user import reset_user_data
from werkzeug.wrappers import Response
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
            for event in workflow.run(document_text=document_text):
                # Handle final event specially
                if event.get("event") == "final":
                    # The final data is a list of ParsedDocumentSection
                    final_sections: List[ParsedDocumentSection] = cast(List[ParsedDocumentSection], [
                        ParsedDocumentSection.model_validate(s) if isinstance(s, dict) else s
                        for s in event.get("data", [])
                    ])
                    # Optionally: do something with the final_sections (e.g., store in DB)
                    print("Final parsed sections:", final_sections)

                # Always yield SSE formatted string
                yield f"data: {json.dumps(event)}\n\n"

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
