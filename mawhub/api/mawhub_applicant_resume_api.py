import json
from typing import List
from frappe import _
import frappe
from mawhub.app.job.dto.applicant_resume import  ApplicantResumeDTO
from mawhub.bootstrap import app_container
from werkzeug.wrappers import Response

from mawhub.pkg.pdfconvertor.pdfconvertor import extract_text_from_pdf  # <--- Correct Import

@frappe.whitelist(methods=["POST"])
def applicant_resume_parse(path: str):
    # Ensure this runs before the stream starts
    resume_text = ""
    try:
        resume_text = extract_text_from_pdf(path)
    except Exception as e:
        frappe.throw(f"Failed to read PDF: {str(e)}")

    def sse_generator():
        workflow = app_container.job_usecase.resume_agent
        try:
            # Iterate properly over the workflow
            yield f"data: Proccessing\n\n"
            if resume_text == "":
                raise frappe.ValidationError("cant parse the resume text")
            for update in workflow.run(resume_text , model_overrides={
                "labeler": "gemini-2.0-flash",
            }):
                yield f"data: {json.dumps(update)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'status': 'error', 'message': str(e)})}\n\n"

    # PASS THE GENERATOR DIRECTLY HERE
    response = Response(sse_generator(), mimetype="text/event-stream")

    # Required headers for SSE
    response.headers.add("Cache-Control", "no-cache")
    response.headers.add("X-Accel-Filtering", "no") # Crucial for Nginx

    return response

@frappe.whitelist(methods=["POST"])
def applicant_resume_create_update(payload: ApplicantResumeDTO):
    return app_container.job_usecase.applicant_resume.applicant_resume_create_update(payload=payload)

@frappe.whitelist(methods=["POST"])

@frappe.whitelist(methods=["POST"])
def applicant_resume_bulk_create(payload: List[ApplicantResumeDTO]):
    return app_container.job_usecase.applicant_resume.applicant_resume_bulk_create(payload=payload)
#     """
#     Create or update Applicant Resume by job_applicant
#     """
#     job_applicant = payload.get("job_applicant")
#     if not job_applicant:
#         frappe.throw(_("job_applicant is required"))
#
#     # Check if resume already exists
#     existing = frappe.get_all(
#         "Applicant Resume",
#         filters={"job_applicant": job_applicant},
#         pluck="name",
#         limit=1,
#     )
#
#     if existing:
#         doc = frappe.get_doc("Applicant Resume", existing[0])
#     else:
#         doc = frappe.new_doc("Applicant Resume")
#         doc.set('job_applicant' , job_applicant)
#
#     # Simple fields
#     for field in [
#         "skills",
#         "summary",
#         "raw_resume_text",
#         "raw_resume_json",
#     ]:
#         if field in payload:
#             doc.set(field, payload.get(field))
#
#     # Child tables
#     _set_child_table(doc, "experience", payload.get("experience"))
#     _set_child_table(doc, "education", payload.get("education"))
#     _set_child_table(doc, "projects", payload.get("projects"))
#     _set_child_table(doc, "links", payload.get("links"))
#
#     doc.save(ignore_permissions=True)
#     frappe.db.commit()
#
#     return {
#         "name": doc.name,
#         "job_applicant": doc.get('job_applicant'),
#     }
# def _set_child_table(doc, fieldname, rows):
#     if rows is None:
#         return
#
#     doc.set(fieldname, [])
#     for row in rows:
#         doc.append(fieldname, row)
#
# def insert_applicant_with_resume(payload: dict):
#     """
#     Inserts Job Applicant and Applicant Resume with child tables
#     Handles rollback on errors
#     """
#     try:
#         frappe.db.begin()  # Start transaction
#
#         # -------------------------------
#         # 1️⃣ Insert Job Applicant
#         # -------------------------------
#         personal = payload.get("personal", {})
#         email = personal.get("email")
#         if not email:
#             frappe.throw(_("Job Applicant email is required"))
#
#         # Check if applicant already exists
#         existing_applicant = frappe.db.exists("Job Applicant", email)
#         if existing_applicant:
#             applicant = frappe.get_doc("Job Applicant", existing_applicant)
#         else:
#             applicant = frappe.new_doc("Job Applicant")
#             applicant.applicant_name = personal.get("name")
#             applicant.email_id = email
#             applicant.phone_number = personal.get("phone")
#             applicant.status = "Open"
#             applicant.creation = now_datetime()
#             applicant.insert(ignore_permissions=True)
#
#         # -------------------------------
#         # 2️⃣ Insert Applicant Resume
#         # -------------------------------
#         resume = frappe.new_doc("Applicant Resume")
#         resume.job_applicant = applicant.name
#         resume.skills = payload.get("skills", {}).get("content")
#         resume.summary = payload.get("summary", {}).get("content")
#         resume.raw_resume_text = ""  # optional: you can join all text
#         resume.raw_resume_json = frappe.as_json(payload)
#
#         # Helper to populate child tables
#         def _set_child_table(doc, fieldname, items):
#             if not items:
#                 return
#             doc.set(fieldname, [])
#             for row in items:
#                 doc.append(fieldname, row)
#
#         # Experience
#         _set_child_table(resume, "experience", payload.get("experience", {}).get("items"))
#         # Education
#         _set_child_table(resume, "education", payload.get("education", {}).get("items"))
#         # Projects
#         _set_child_table(resume, "projects", payload.get("projects", {}).get("items"))
#         # Links
#         links = personal.get("links", [])
#         _set_child_table(resume, "links", [{"url": l} for l in links])
#
#         resume.insert(ignore_permissions=True)
#
#         frappe.db.commit()  # Commit transaction
#         return {
#             "success": True,
#             "job_applicant": applicant.name,
#             "resume": resume.name,
#         }
#
#     except Exception as e:
#         frappe.db.rollback()  # Rollback on any error
#         frappe.log_error(message=str(e), title="Insert Applicant + Resume Failed")
#         return {
#             "success": False,
#             "error": str(e)
#         }
#
# @frappe.whitelist(methods=["POST", "PUT"], allow_guest=True)
# def job_applicant_create(payload: str) -> dict:
#     """
#     1. Extract text from PDF
#     2. Run AI to parse resume
#     3. Check if Job Applicant exists by email
#     4. Create Job Applicant if not exists
#     5. Create/Update Applicant Resume linked to Job Applicant
#     """
#     # 1️⃣ Extract text
#     txt = extract_text_from_pdf(payload)
#
#     # 2️⃣ Parse resume with AI
#     workflow = ResumeWorkflow()
#     final_json = workflow.run(txt)
#     parsed_data = {k: v.model_dump() for k, v in final_json.items()}
#     try:
#
#         return insert_applicant_with_resume(parsed_data)
#     except Exception as e:
#         raise e
#     personal_info = parsed_data.get("personal", {})
#     email = personal_info.get("email")
#     name = personal_info.get("name")
#
#     if not email:
#         frappe.throw(_("Cannot find email in resume to link Job Applicant"))
#
#     # 3️⃣ Check if Job Applicant exists
#     doc_applicant= frappe.get_doc(
#         "Job Applicant",
#         email,
#     )
#
#     if doc_applicant is None:
#         doc_applicant = frappe.new_doc("Job Applicant")
#         doc_applicant.name = email
#         doc_applicant.applicant_name = name
#         # You can add more base info from AI if available
#         doc_applicant.save(ignore_permissions=True)
#         job_applicant_name = doc_applicant.name
#
#     # 5️⃣ Create/Update Applicant Resume
#     # Check if resume already exists
#     existing_resume = frappe.get_all(
#         "Applicant Resume",
#         filters={"job_applicant": job_applicant_name},
#         pluck="name",
#         limit=1
#     )
#
#     if existing_resume:
#         doc_resume = frappe.get_doc("Applicant Resume", existing_resume[0])
#     else:
#         doc_resume = frappe.new_doc("Applicant Resume")
#         doc_resume.job_applicant = job_applicant_name
#
#     # Set simple fields
#     for field in ["skills", "summary"]:
#         if field in parsed_data:
#             doc_resume.set(field, parsed_data[field].get("content"))
#
#     # Store raw text and raw json
#     doc_resume.raw_resume_text = txt
#     doc_resume.raw_resume_json = json.dumps(parsed_data, indent=2)
#
#     # Child tables
#     _set_child_table(doc_resume, "experience", parsed_data.get("experience", {}).get("items"))
#     _set_child_table(doc_resume, "education", parsed_data.get("education", {}).get("items"))
#     _set_child_table(doc_resume, "projects", parsed_data.get("projects", {}).get("items"))
#     _set_child_table(doc_resume, "links", personal_info.get("links"))
#
#     doc_resume.save(ignore_permissions=True)
#     frappe.db.commit()
#
#     return {
#         "job_applicant": job_applicant_name,
#         "resume": doc_resume.name,
#         "email": email,
#         "parsed_data": parsed_data
#     }
#
