from __future__ import annotations
import json
from typing import TYPE_CHECKING, List, Optional, Dict, cast,Tuple

import frappe
from frappe import _
from frappe.utils import now_datetime
from hrms.hr.doctype.job_opening.job_opening import JobOpening

from mawhub.app.job.dto.job_opening_dto import JobPipelineStepApplicantDTO, JobPipelineStepDTO
from mawhub.mawhub.doctype.parsed_document.parsed_document import ParsedDocument

if TYPE_CHECKING:
    from frappe.model.document import Document

class JobLinkError(Exception): ...

class CustomJobOpening(JobOpening):

    # -------------------------------------------------
    # lifecycle
    # -------------------------------------------------

    @classmethod
    def get_list(cls, filters=None, fields=None, limit_start=0, limit_page_length=20, order_by=None, as_dict=False, debug=False):
        return []
    @frappe.whitelist()
    def fetch_job_info(self):
        steps_rows = self.get("custom_pipeline_steps") or []
        applicants_rows = self.get("custom_applicants") or []
        frappe.publish_realtime(
                event="job_info_progress",
                message={"status": "started"},
                user=frappe.session.user
            )

        # -------------------------
        # step index
        # -------------------------
        step_id_to_row = {s.step_code: s for s in steps_rows}

        # -------------------------
        # group applicants by step_code
        # -------------------------
        steps_map: Dict[str, List[JobPipelineStepApplicantDTO]] = {
                "All" : []
        }

        for a in applicants_rows:
            step_row = step_id_to_row.get(a.get("step_code"))
            if not step_row:
                continue
            if a.get("invalidated_at"):
                continue

            step_code = step_row.get("step_code")

            dto: JobPipelineStepApplicantDTO = {
                "name": a.get("name"),
                "job_applicant": a.get("job_applicant"),
                "applicant_resume": a.get("applicant_resume"),
                "comment": a.get("comment") or "",
            }
            steps_map['All'].append(dto)
            steps_map.setdefault(step_code, []).append(dto)

        # -------------------------
        # steps list
        # -------------------------
        steps: List[JobPipelineStepDTO] = [{
                "name": 'All',
                "step_code": "All",
                "step_name": "All",
                "step_type": "All",
                "step_idx": len(steps_map['All']),
                "applicant_count": len(applicants_rows),
            }]

        for s in steps_rows:
            step_code = s.get("step_code")

            steps.append({
                "name": s.get("name"),
                "step_code": step_code,
                "step_name": s.get("step_name"),
                "step_type": s.get("step_type"),
                "step_idx": s.get("idx"),
                "applicant_count": len(steps_map.get(step_code, [])),
            })

        # -------------------------
        # salary ranges
        # -------------------------
        lower_range = self.get("lower_range")
        upper_range = self.get("upper_range")
        docs = frappe.get_all(
                "Parsed Document" ,
                filters={
                    "request_id" : self.get("custom_parse_request_id")
                    },
                fields=["name" , "file_path" ,  "metadata" ],
                )

        parsed_docs = []
        for doc in docs:
            doc["sections"] = frappe.get_all(
                "Parsed Document Section",
                filters={"parent": doc["name"]},
                fields=["title" , "description" , "bullet_points" , "footer" , "is_number_list"],
                order_by="idx asc",
            )
            parsed_docs.append(doc)
        # lower_range = str(lower_obj.get("parsedValue", ""))
        # upper_range = str(upper_obj.get("parsedValue", ""))

        # -------------------------
        # final DTO
        # -------------------------
        return {
                "name": self.get("name"),
                "designation": self.get("designation"),
                "department": self.get("department"),
                "pipeline": self.get("custom_pipeline"),
                "parsed_documents": parsed_docs,
                "employment_type": self.get("employment_type") or "",
                "location": self.get("location") or "",
                "customer": self.get("custom_customer") or "",
                "docstatus": self.get("docstatus"),
                "publish": self.get("publish"),
                "publish_salary_range": self.get("publish_salary_range"),
                "publish_applications_received": self.get("publish_applications_received"),
                "currency": self.get("currency"),
                "salary_per": self.get("salary_per"),
                "lower_range": lower_range,
                "upper_range": upper_range,
                "posted_on": str(self.get("posted_on")),
                "closes_on": str(self.get("closes_on") or ""),
                "step_count": len(steps),
                "applicants_count": len(applicants_rows),
                "steps": steps,
                "steps_map": steps_map,
                }
    def sync_pipeline_steps(self):
        pipeline_name = self.get("custom_pipeline")
        if not pipeline_name:
            return

        pipeline_doc = frappe.get_doc("Job Pipeline", str(pipeline_name))

        source_steps = pipeline_doc.get("steps") or []
        if not source_steps:
            return

        # rebuild table (simplest + safest)
        self.set("custom_pipeline_steps", [])

        for step in source_steps:
            self.append("custom_pipeline_steps", {
                "step_name": step.get("step_name"),
                "step_code": step.get("step_code"),
                "step_type": step.get("step_type"),
                # copy only the fields that actually exist in Pipeline Step child doctype
            })
    def before_save(self) -> None:
        self.ensure_project()
        if self.is_new():
            self.sync_pipeline_steps()
            return

        # self.handle_applicant_invalidation()


    def job_find_document(self) -> ParsedDocument | None:
        parsed_request_id = str(self.get("custom_parse_request_id" , ""))
        parsed_document_name = frappe.db.exists({
            "doctype" : "Parsed Document",
            "request_id" : parsed_request_id
            })
        if not isinstance(parsed_document_name,str):
            return None
        parsed_document = frappe.get_doc("Parsed Document" , parsed_document_name)
        if not parsed_document:
            return None
        meta = parsed_document.get("metadata")
        if isinstance(meta,str):
            parsed_document.set("metadata" , json.loads(meta))
        return cast(ParsedDocument , parsed_document)

    # -------------------------------------------------
    # project
    # -------------------------------------------------

    def ensure_project(self) -> None:
        project_name = self.get("job_title")
        if not project_name:
            return

        existing = frappe.db.exists({ "doctype" :"Project", "project_name" : project_name})
        if existing:
            self.project = existing
            return

        project: Document = frappe.get_doc({
            "doctype": "Project",
            "project_name": project_name,
            "project_template": "Job Opening",
            "status": "Open",
            })

        project.insert(ignore_permissions=True)
        self.project = project.name

    # -------------------------------------------------
    # pipeline step helpers
    # -------------------------------------------------

    def get_pipeline_steps(self) -> List[Document]:
        steps = self.get("custom_pipeline_steps")
        if not isinstance(steps, list):
            return []
        return steps

    def get_default_step_name(self) -> str:
        steps: List[Document] = self.get_pipeline_steps()
        if not steps:
            frappe.throw(_("Job Opening has no pipeline steps"))
        return str(steps[0].get("step_code"))

    def find_step_by_code(self, step_code: str) -> Optional[Document]:
        steps: List[Document] = self.get_pipeline_steps()

        return next(
                (s for s in steps if getattr(s, "step_code", None) == step_code),
                None
                )

    def resolve_step_code(self, step_code: Optional[str]) -> str:
        if not step_code or step_code in ("" ,"null", "all","All"):
            return self.get_default_step_name()
        return step_code

    # -------------------------------------------------
    # applicant table helpers
    # -------------------------------------------------

    def get_applicant_rows(self) -> List[Document]:
        rows = self.get("custom_applicants")
        if not isinstance(rows, list):
            return []
        return rows

    def get_active_applicant_row(self, applicant_id: str) -> Optional[Document]:
        rows: List[Document] = self.get_applicant_rows()

        return next(
                (
                    r for r in rows
                    if r.get("job_applicant") == applicant_id
                    and not r.get("invalidated_at")
                    ),
                None
                )

    def job_find_by_applicant(self,applicant_id:str):
        response = {"job_opening" : self.as_dict()}
        parsed_document = self.job_find_document()
        if parsed_document:
            response["parsed_document"] = parsed_document.as_dict()
        job_applicant_doc , job_applicant_resume_doc = self.get_active_applicant_row_with_resume(applicant_id)
        if not job_applicant_doc:
            return response
        response["job_applicant"] = job_applicant_doc.as_dict()
        if not job_applicant_resume_doc:
            return response
        response["applicant_resume"] = job_applicant_resume_doc.as_dict()
        return response

    def get_active_applicant_row_with_resume(self, applicant_id: str) -> Tuple[Optional[Document],Optional[Document]]:
        job_applicant_doc = self.get_active_applicant_row(applicant_id)
        if not job_applicant_doc:
            return None,None
        applicant_resume = job_applicant_doc.get("applicant_resume" , "")
        if not isinstance(applicant_resume ,str):
            return job_applicant_doc , None

        applicant_resume_doc = frappe.get_doc("Applicant Resume" , applicant_resume)
        if not applicant_resume_doc:
            return job_applicant_doc , None
        return job_applicant_doc , applicant_resume_doc

    # -------------------------------------------------
    # single applicant operations
    # -------------------------------------------------

    @frappe.whitelist()
    def link_applicant_to_step(
            self,
            applicant_id: str,
            step_code: Optional[str],
            resume_id: str,
            comment: Optional[str] = None,
            ) -> Document:
        step: str = self.resolve_step_code(step_code)
        print("Step is " , step)
        if not isinstance(self.get("custom_applicants"), list):
            self.set("custom_applicants", [])

        existing: Optional[Document] = self.get_active_applicant_row(applicant_id)
        print("Existing is " , existing)

        if existing:
            if existing.get("step_code") == step:
                raise JobLinkError(f"Applicant: {applicant_id} is already on this step :{step_code}")
            existing.set("invalidated_at", now_datetime())
            existing.set("invalidated_by", frappe.session.user)

        new_row: Document = self.append("custom_applicants", {
            "job_applicant": applicant_id,
            "step_code": step,
            "applicant_resume": resume_id,
            "comment": comment,
            })

        print("New Row is " , new_row)
        self.save()
        print("Step is " , new_row)
        frappe.db.commit()
        return new_row

    @frappe.whitelist()
    def remove_applicant_from_step(
            self,
            applicant_id: str,
            comment: Optional[str] = None
            ) -> bool:
        row: Optional[Document] = self.get_active_applicant_row(applicant_id)
        if not row:
            return False

        row.set("invalidated_at", now_datetime())
        row.set("invalidated_by", frappe.session.user)

        if comment:
            row.set("comment", comment)
        self.save()
        frappe.db.commit()
        return True



    @frappe.whitelist()
    def copy_applicant_to_another_job(
            self,
            applicant_id: str,
            new_job_name: str,
            new_step_code: str,
            comment: Optional[str] = None
            ):
        row: Optional[Document] = self.get_active_applicant_row(applicant_id)
        if not row:
            raise frappe.ValidationError(_("Applicant not exists on this job"))

        resume_id  = row.get("applicant_resume")
        new_job = frappe.get_doc("Job Opening" , new_job_name)
        if not new_job:
            raise frappe.NotFound("destination_job_not_found")
        new_job_doc = cast(CustomJobOpening, new_job)
        new_job_doc.link_applicant_to_step(
                applicant_id=applicant_id,
                step_code=new_step_code,
                resume_id=str(resume_id),
                comment=comment
                )
        new_job_doc.save()
        frappe.db.commit()
        print("new_job is" , new_job_doc.get("custom_applicants"))
        return row
    @frappe.whitelist()
    def move_applicant_to_another_job(
            self,
            applicant_id: str,
            new_job_name: str,
            new_step_code: str,
            comment: Optional[str] = None
            ):
        applicant_row = self.copy_applicant_to_another_job(applicant_id,new_job_name,new_step_code,comment)
        applicant_row.set("invalidated_at", now_datetime())
        applicant_row.set("invalidated_by", frappe.session.user)
        self.save()
        frappe.db.commit()
        print(applicant_row)
        return applicant_row

    @frappe.whitelist()
    def move_applicants_to_another_job(
            self,
            applicant_ids: List[str],
            new_job_name: str,
            new_step_code: str,
            comment: Optional[str] = None
            ):
        moved_rows = []

        for applicant_id in applicant_ids or []:
            row = self.move_applicant_to_another_job(
                applicant_id=applicant_id,
                new_job_name=new_job_name,
                new_step_code=new_step_code,
                comment=comment
            )
            if row:
                moved_rows.append(row)

        return moved_rows


    @frappe.whitelist()
    def copy_applicants_to_another_job(
            self,
            applicant_ids: List[str],
            new_job_name: str,
            new_step_code: str,
            comment: Optional[str] = None
            ):
        copied_rows = []

        for applicant_id in applicant_ids or []:
            row = self.copy_applicant_to_another_job(
                applicant_id=applicant_id,
                new_job_name=new_job_name,
                new_step_code=new_step_code,
                comment=comment
            )
            if row:
                copied_rows.append(row)

        return copied_rows

        # return new_row
    @frappe.whitelist()
    def move_applicant_to_another_step(
            self,
            applicant_id: str,
            new_step_code: str,
            comment: Optional[str] = None
            ) -> Document:
        new_step: str = self.resolve_step_code(new_step_code)

        row: Optional[Document] = self.get_active_applicant_row(applicant_id)
        if not row:
            raise frappe.ValidationError(_("Applicant not exists on this job"))

        resume_id  = row.get("applicant_resume")

        row.set("invalidated_at", now_datetime())
        row.set("invalidated_by", frappe.session.user)

        new_row: Document = self.append("custom_applicants", {
            "job_applicant": applicant_id,
            "step_code": new_step,
            "applicant_resume": resume_id,
            "comment": comment,
            })
        self.save()
        frappe.db.commit()
        return new_row

    # -------------------------------------------------
    # bulk operations
    # -------------------------------------------------

    @frappe.whitelist()
    def link_applicants_to_step(
            self,
            applicant_ids: List[str],
            step_code: Optional[str],
            resume_map: Dict[str, str],
            comment: Optional[str] = None,
            ) -> List[Document]:

        created: List[Document] = []

        for applicant_id in applicant_ids:
            resume_id: Optional[str] = resume_map.get(applicant_id)
            if not resume_id:
                raise frappe.ValidationError(_(f"Missing resume for {applicant_id}"))

            row = self.link_applicant_to_step(
                    applicant_id,
                    step_code,
                    resume_id,
                    comment,
                    )
            created.append(row)

        return created

    @frappe.whitelist()
    def remove_applicants_from_step(
            self,
            applicant_ids: List[str],
            comment: Optional[str] = None
            ) -> int:
        count: int = 0

        for applicant_id in applicant_ids:
            if self.remove_applicant_from_step(applicant_id, comment):
                count += 1

        return count

    @frappe.whitelist()
    def move_applicants_to_another_step(
            self,
            applicant_ids: List[str],
            new_step_code: str,
            comment: Optional[str] = None
            ) -> List[Document]:

        moved: List[Document] = []

        for applicant_id in applicant_ids:
            moved.append(
                    self.move_applicant_to_another_step(
                        applicant_id,
                        new_step_code,
                        comment,
                        )
                    )

        return moved


    # -------------------------------------------------
    # validation
    # -------------------------------------------------

    def validate_custom_applicants(self) -> None:
        active: Dict[str, bool] = {}

        valid_steps  = [
                d.name for d in self.get_pipeline_steps()
                ]

        for idx, row in enumerate(self.get_applicant_rows()):
            if row.get("invalidated_at"):
                continue
            applicant_resume = row.get("applicant_resume")
            resume_owner = frappe.db.get_value(
                    "Applicant Resume",
                    str(applicant_resume),
                    "job_applicant"
                    )

            if resume_owner != row.get("job_applicant"):
                frappe.throw(_(
                    "Row #{0}: Resume does not belong to Applicant"
                    ).format(idx + 1))

            applicant_id = row.get("job_applicant")

            if applicant_id in active:
                frappe.throw(_(
                    "Row #{0}: Duplicate active applicant"
                    ).format(idx + 1))

            active[str(applicant_id)] = True

            if valid_steps and row.get("step") not in valid_steps:
                raise frappe.ValidationError(_(
                    "Row #{0}: Invalid step"
                    ).format(idx + 1))

    # -------------------------------------------------
    # invalidation tracker
    # -------------------------------------------------

    # def handle_applicant_invalidation(self) -> None:
    #     old_doc: Optional[Document] = self.get_doc_before_save()
    #     if not old_doc:
    #         return
    #
    #     if not self.has_value_changed("custom_applicants"):
    #         return
    #
    #     new_rows = self.get("custom_applicants")
    #     old_rows = old_doc.get("custom_applicants")
    #
    #     if not isinstance(new_rows, list) or not isinstance(old_rows, list):
    #         return
    #
    #     new_names = {r.name for r in new_rows}
    #
    #     for row in old_rows:
    #         if row.name in new_names:
    #             continue
    #
    #         self.append("custom_applicants", {
    #             **row.as_dict(),
    #             "invalidated_at": now_datetime(),
    #             "invalidated_by": frappe.session.user
    #             })

    # -------------------------------------------------
    # history
    # -------------------------------------------------

    def get_applicant_history(self, applicant_id: str) -> List[Document]:
        return [
                r for r in self.get_applicant_rows()
                if r.get("job_applicant") == applicant_id
                ]

