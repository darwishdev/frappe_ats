
from mawhub.mawhub.doctype.parsed_document.parsed_document import ParsedDocumentDBModel
from mawhub.pkg.pdfconvertor.pdfconvertor import extract_text_from_pdf
import frappe
from mawhub.bootstrap import app_container

@frappe.whitelist(methods=["PUT" , "POST"], allow_guest=True)
def parsed_document_create_update(payload:ParsedDocumentDBModel):
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
            request_id=request_id,
            user=frappe.session.user
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
            request_id=request_id,
            user=frappe.session.user
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
def parsed_document_parse_bg(file_path:str ,document_text: str, request_id: str,user:str):
    if document_text == "":
        document_text = extract_text_from_pdf(file_path)
    events = app_container.job_usecase.parsed_document.parse_document(file_path,document_text,request_id)
    for event in events:
        frappe.publish_realtime(
            event=f"document_parser",
            message=event,
            user=user
        )
    #
