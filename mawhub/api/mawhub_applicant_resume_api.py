import json
from typing import Iterator, List, cast
from frappe import _
import frappe
from mawhub.app.job.dto.applicant_resume import  ApplicantResumeDTO
from mawhub.app.job.dto.job_applicant import JobApplicantCreateWithResume
from mawhub.bootstrap import app_container
from werkzeug.wrappers import Response


@frappe.whitelist(methods=["POST","GET"])
def applicant_resume_parse(path: str,job_opening_id: str, pipeline_step_id: str):
    def sse_stream() -> Iterator[str]:
        try:
            # Use the new typed usecase method
            for event in app_container.job_usecase.applicant_resume.applicant_resume_parse(
                path,
            ):
                if event["event"] == 'final' :
                    data = event['data']
                    params : JobApplicantCreateWithResume = {
                        "job_opening_id" : job_opening_id,
                        "pipeline_step_id" : pipeline_step_id,
                        "applicant_resume" : cast(ApplicantResumeDTO , data)
                    }
                    try:
                        app_container.job_usecase.applicant_resume.job_applicant_create_with_resume(params)
                    except Exception as e:
                        raise frappe.ValidationError(f"error creating the applicant on db {str(e)
                    } with data {json.dumps(data)}")
                    print(event['data'])
                yield f"data: {json.dumps(event)}\n\n"
        except Exception as e:
            # Final SSE error event
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

@frappe.whitelist(methods=["POST", "GET"])
def applicant_resume_create_update(payload: ApplicantResumeDTO):
    return app_container.job_usecase.applicant_resume.applicant_resume_create_update(payload=payload)

@frappe.whitelist(methods=["POST", "GET"])

@frappe.whitelist(methods=["POST", "GET"])
def applicant_resume_bulk_create(payload: List[ApplicantResumeDTO]):
    return app_container.job_usecase.applicant_resume.applicant_resume_bulk_create(payload=payload)
