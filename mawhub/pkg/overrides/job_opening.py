from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional, Dict

import frappe
from frappe import _
from frappe.utils import now_datetime
from hrms.hr.doctype.job_opening.job_opening import JobOpening

if TYPE_CHECKING:
    from frappe.model.document import Document


class CustomJobOpening(JobOpening):

    # -------------------------------------------------
    # lifecycle
    # -------------------------------------------------

    @frappe.whitelist()
    def fetch_job_info(self):
        job_info = self.as_dict()
        return job_info
    def before_save(self) -> None:
        if self.is_new():
            return

        self.handle_applicant_invalidation()
        self.ensure_project()

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
        return str(steps[0].name)

    def find_step_by_code(self, step_code: str) -> Optional[Document]:
        steps: List[Document] = self.get_pipeline_steps()

        return next(
            (s for s in steps if getattr(s, "step_code", None) == step_code),
            None
        )

    def resolve_step_name(self, step_code: Optional[str]) -> str:
        if not step_code or step_code in ("null", "all"):
            return self.get_default_step_name()

        step: Optional[Document] = self.find_step_by_code(step_code)
        if not step:
            err = _(f"Step code '{step_code}' not found in pipeline")
            raise frappe.ValidationError(err)

        return str(step.name)

    # -------------------------------------------------
    # applicant table helpers
    # -------------------------------------------------

    def get_applicant_rows(self) -> List[Document]:
        rows = self.get("custom_applicants")
        if not isinstance(rows, list):
            return []
        return rows

    def _get_active_applicant_row(self, applicant_id: str) -> Optional[Document]:
        rows: List[Document] = self.get_applicant_rows()

        return next(
            (
                r for r in rows
                if r.get("job_applicant") == applicant_id
                and not r.get("invalidated_at")
            ),
            None
        )

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
        step_name: str = self.resolve_step_name(step_code)

        if not isinstance(self.get("custom_applicants"), list):
            self.set("custom_applicants", [])

        existing: Optional[Document] = self._get_active_applicant_row(applicant_id)

        if existing:
            existing.set("invalidated_at", now_datetime())
            existing.set("invalidated_by", frappe.session.user)

        new_row: Document = self.append("custom_applicants", {
            "job_applicant": applicant_id,
            "step": step_name,
            "applicant_resume": resume_id,
            "comment": comment,
        })

        return new_row

    @frappe.whitelist()
    def remove_applicant_from_step(
        self,
        applicant_id: str,
        comment: Optional[str] = None
    ) -> bool:
        row: Optional[Document] = self._get_active_applicant_row(applicant_id)
        if not row:
            return False

        row.set("invalidated_at", now_datetime())
        row.set("invalidated_by", frappe.session.user)

        if comment:
            row.set("comment", comment)

        return True

    @frappe.whitelist()
    def move_applicant_to_another_step(
        self,
        applicant_id: str,
        new_step_code: str,
        comment: Optional[str] = None
    ) -> Document:
        step_name: str = self.resolve_step_name(new_step_code)

        row: Optional[Document] = self._get_active_applicant_row(applicant_id)
        if not row:
            raise frappe.ValidationError(_("Applicant not exists on this job"))

        resume_id  = row.get("applicant_resume")

        row.set("invalidated_at", now_datetime())
        row.set("invalidated_by", frappe.session.user)

        new_row: Document = self.append("custom_applicants", {
            "job_applicant": applicant_id,
            "step": step_name,
            "applicant_resume": resume_id,
            "comment": comment,
        })

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

    def handle_applicant_invalidation(self) -> None:
        old_doc: Optional[Document] = self.get_doc_before_save()
        if not old_doc:
            return

        if not self.has_value_changed("custom_applicants"):
            return

        new_rows = self.get("custom_applicants")
        old_rows = old_doc.get("custom_applicants")

        if not isinstance(new_rows, list) or not isinstance(old_rows, list):
            return

        new_names = {r.name for r in new_rows}

        for row in old_rows:
            if row.name in new_names:
                continue

            self.append("custom_applicants", {
                **row.as_dict(),
                "invalidated_at": now_datetime(),
                "invalidated_by": frappe.session.user
            })

    # -------------------------------------------------
    # history
    # -------------------------------------------------

    def get_applicant_history(self, applicant_id: str) -> List[Document]:
        return [
            r for r in self.get_applicant_rows()
            if r.get("job_applicant") == applicant_id
        ]
