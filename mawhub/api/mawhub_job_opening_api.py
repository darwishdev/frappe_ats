import json
from typing import Iterator, List
import frappe
from frappe import _
from werkzeug.wrappers import Response

from mawhub.app.job.dto.job_opening import JobOpeningDTO
from mawhub.bootstrap import app_container


@frappe.whitelist(methods=["GET" , "POST"], allow_guest=True)
def job_opening_parse(path:str):
    def sse_stream() -> Iterator[str]:
        try:
            # Use the new typed usecase method
            for event in app_container.job_usecase.job_opening.job_opening_parse(
                path,
            ):
                yield f"data: {json.dumps(event)}\n\n"
        except Exception as e:
            error_event  = {
                "event": "error",
                "data": str(e),
            }
            yield f"data: {json.dumps(error_event)}\n\n"

    # 3️⃣ Return a proper SSE Response
    response = Response(sse_stream(), mimetype="text/event-stream")

    # 4️⃣ Required headers for SSE to work properly
    response.headers.add("Cache-Control", "no-cache")
    response.headers.add("X-Accel-Buffering", "no")  # Crucial for Nginx buffering

    return response
@frappe.whitelist(methods=["GET" , "POST"], allow_guest=True)
def job_opening_list()->List[JobOpeningDTO]:
    return app_container.job_usecase.job_opening.job_opening_list("Administrator")


@frappe.whitelist(methods=["GET" , "POST"], allow_guest=True)
def job_opening_find(job:str)->JobOpeningDTO:
    return app_container.job_usecase.job_opening.job_opening_find(job)
