
from concurrent.futures import ThreadPoolExecutor
import json
from time import sleep

from frappe.twofactor import enqueue
from mawhub.api.mawhub_job_opening_api import job_opening_parse
from mawhub.pkg.pdfconvertor.pdfconvertor import extract_text_from_pdf
from mawhub.sqltypes.table_models import JobOpening
import frappe
from werkzeug.wrappers import Response
from mawhub.app.job.dto.parsed_document_dto import ParsedDocumentDTO, ParsedDocumentParseRequest
from mawhub.bootstrap import app_container


@frappe.whitelist(methods=["PUT" , "POST"], allow_guest=True)
def parsed_document_create_update(payload:ParsedDocumentDTO):
    return app_container.job_usecase.parsed_document.parsed_document_create_update(payload)

@frappe.whitelist(methods=["POST", "GET"], allow_guest=True)
def parsed_document_parse(path: str):
    """
    Endpoint: enqueue background job to parse document.
    Returns immediately with acknowledgment.
    """
    print("recieved a new request")
    request_id = frappe.generate_hash(length=12)
    full_text = extract_text_from_pdf(path)


    try:

        # Enqueue background job
        frappe.enqueue(
            method=parsed_document_parse_bg,  # String path
            queue="long",
            timeout=800,
            is_async=True,
            now=False,
            enqueue_after_commit=False,
            at_front=True,
            file_path=path,
            document_text=full_text,
            request_id=request_id
        )
        frappe.enqueue(
            method="mawhub.api.mawhub_job_opening_api.job_opening_parse",
            queue="short",
            timeout=800,
            is_async=True,
            now=False,
            enqueue_after_commit=False,
            at_front=True,
            file_path=path,
            document_text=full_text,
            request_id=request_id
        )

        return {
            "status": "queued",
            "request_id": request_id,
            "message": "Document parsing started"
        }

    except Exception as e:
        # Return error response
        return {
            "status": "error",
            "request_id": request_id,
            "message": f"Failed to enqueue job: {str(e)}"
        }
@frappe.whitelist(methods=["POST", "GET"], allow_guest=True)
def parsed_document_parse_bg(file_path:str ,document_text: str, request_id: str):
    print("bg loadeddd")
    if document_text == "":
        document_text = extract_text_from_pdf(file_path)
    return app_container.job_usecase.parsed_document.parse_document(file_path,document_text,request_id),
    future_doc =executor.submit(
        full_text
    )
    future_job = executor.submit(
        app_container.job_usecase.job_opening.job_opening_parse,
        full_text
    )
    # with ThreadPoolExecutor(max_workers=2) as executor:
    #     # Submit both tasks
    #
    #     # Wait for both to complete and get results
    #     doc = future_doc.result()
    #     job = future_job.result()

    return "bye"
    # payload : ParsedDocumentParseRequest = {
    #     "path" : path,
    #     "parent_type" : parent_type,
    #     "parent_id" : parent_id
    # }
    full_text = extract_text_from_pdf(path)
    doc =  app_container.job_usecase.parsed_document.parse_document(full_text)
    job =  app_container.job_usecase.job_opening.job_opening_parse(full_text)
    return "bye"
    # for event in agent_events:
    #     print("event is")
    #     print(event)
    #     if event["event"] == "final":
    #         return event["data"]
    #     # full_parsed_document[event[event]]




# @frappe.whitelist(methods=["POST", "GET"], allow_guest=True)
# def parsed_document_parse_bg(path: str, parent_type: str, parent_id: str, request_id: str):
#     print("path:", path)
#     print("parent_type:", parent_type)
#     print("parent_id:", parent_id)
#     print("request_id:", request_id)
#     frappe.db.sql("""UPDATE `tabJob Opening` SET description = 'naaaa' """ )
#     frappe.db.commit()
# @frappe.whitelist(methods=["POST", "GET"], allow_guest=True)
# def parsed_document_parse(path: str,parent_type: str, parent_id: str):
#     payload : ParsedDocumentParseRequest = {
#         "path" : path,
#         "parent_type" : parent_type,
#         "parent_id" : parent_id
#     }
#     def final_event_callback(final_event: dict)->str:
#         try:
#             # Initialize the LLM agent
#
#             # Run the agent to get JobOpeningSchema
#             job_event = app_container.job_usecase.job_agent.run(final_event)
#             job_opening_create_params : JobOpening = {
#                 "name": "",  # required for new doc
#                 "job_title": job_event["job_title"] or "Untitled",
#                 "designation": job_event.get("designation") or job_event["job_title"],
#                 "custom_customer": job_event.get("customer") or "",
#                 "custom_pipeline": "Main",
#                 "location": job_event.get("location") or "",
#                 "planned_vacancies": job_event.get("planned_vacancies", 1),
#                 "vacancies": job_event.get("vacancies", 1),
#                 "lower_range": job_event.get("lower_range", 0.0),
#                 "upper_range": job_event.get("upper_range", 0.0),
#                 "publish": job_event.get("publish", 1),
#                 "publish_salary_range": job_event.get("publish_salary_range", 1),
#                 "publish_applications_received": job_event.get("publish_applications_received", 1),
#             }
#             try:
#                 job_create_req = app_container.job_usecase.job_opening.job_opening_create_update(job_opening_create_params)
#             except Exception as e:
#                 raise Exception(f"body: {json.dumps(job_opening_create_params)} error :{str(e)}")
#             print(f"final event is hapening here")
#             print(f"final event is hapening here")
#             print(f"final event is hapening here {str(job_create_req.name)}")
#             print(f"final event is hapening here")
#             print(f"final event is hapening here")
#             return str(job_create_req.name)
#
#             # Convert schema to TypedDict event
#             # job_event = job_opening_schema_to_event(job_schema)
#
#             # Call the actual API to create/update job opening
#             # app_container.job_usecase.job_opening_create_update(job_event)
#
#         except Exception as e:
#             frappe.log_error(f"JobOpening creation failed: {str(e)}", "parsed_document_parse")
#             raise Exception(f"Failed to save the job with body : {str(e)}")
#     response = Response(app_container.job_usecase.parsed_document.parse_document(payload,save_parent_callback=final_event_callback), mimetype="text/event-stream")
#     response.headers.update({
#         "Cache-Control": "no-cache",
#         "X-Accel-Buffering": "no",  # Disables Nginx buffering for instant delivery
#         "Connection": "keep-alive"
#     })
#
#     return response
