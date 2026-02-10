from frappe import _
import frappe
from frappe.utils import now_datetime
from hrms.hr.doctype.job_opening.job_opening import JobOpening
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from frappe.model.document import Document
class CustomJobOpening(JobOpening):
    def before_save(self):
        # Run original HRMS logic first if needed
        # if hasattr(super(), "before_save"):
        #     parent_method = getattr(super(), "before_save", None)
        #     if parent_method:
        #         parent_method()

        if self.is_new():
            return

        self.handle_applicant_invalidation()
        self.ensure_project()
        # self.validate_custom_applicants()

    def ensure_project(self):
        project_name = self.get("job_title")
        if not project_name:
            return

        # Check if project already exists
        existing = frappe.db.exists("Project", project_name)
        if existing:
            self.project = existing
            return

        # Create project from template
        project = frappe.get_doc({
            "doctype": "Project",
            "project_name": project_name,
            "project_template": "Job Opening",
            "status": "Open",
        })

        project.insert(ignore_permissions=True)

        # Link back to job opening (requires Link field "project")
        self.project = project.name
    def validate_custom_applicants(self):
        active_applicants = {}  # To track duplicates: {applicant_id: row_index}

        # Get valid steps from the parent field
        valid_steps = [d.name for d in self.get("custom_pipeline_steps") or []]

        for idx, row in enumerate(self.get("custom_applicants") or []):
            # Skip validation for invalidated rows
            if row.invalidated_at:
                continue

            # 1. Validation: Resume must belong to the same Job Applicant
            resume_owner = frappe.db.get_value("Applicant Resume", row.applicant_resume, "job_applicant")
            if resume_owner != row.job_applicant:
                raise Exception(
                    _("Row #{0}: The Resume {1} does not belong to Applicant {2}").format(
                        idx + 1, row.applicant_resume, row.job_applicant
                    )
                )

            # 2. Validation: No duplicate valid records for the same applicant
            if row.job_applicant in active_applicants:
                raise Exception(
                    _("Row #{0}: Applicant {1} already has an active record in this Job Opening.").format(
                        idx + 1, row.job_applicant
                    )
                )
            active_applicants[row.job_applicant] = idx

            # 3. Validation: Step must exist in custom_pipeline_steps
            if valid_steps and row.step not in valid_steps:
                frappe.throw(
                    _("Row #{0}: Step '{1}' is not allowed for this Job Opening. Valid steps: {2}").format(
                        idx + 1, row.step, ", ".join(valid_steps)
                    )
                )
    def handle_applicant_invalidation(self):
        old_doc = self.get_doc_before_save()
        if not old_doc:
            return

        is_applicants_changed = self.has_value_changed("custom_applicants")
        if not is_applicants_changed:
            return
        new_applicants = self.get("custom_applicants")
        old_applicants = old_doc.get("custom_applicants" )
        new_applicants_map = {}

        if isinstance(new_applicants , list):
            for new_applicant in new_applicants:
                new_applicants_map[new_applicant.name] = new_applicant.name

        olds = []
        if not isinstance(old_applicants , list):
            return
        if len(old_applicants) == 0:
            return

        for value in old_applicants:
            olds.append(value.name)
            if value.name in new_applicants_map:
                continue
            self.append("custom_applicants" , {
                **value.as_dict(),
                "invalidated_at" : now_datetime(),
                "invalidated_by" : frappe.session.user
                })
    def get_applicant_history(self, applicant_id):
        """Returns all rows (active and invalid) for one applicant"""
        applicants = self.get("custom_applicants" , filters={"job_applicant":applicant_id},default=[])
        return applicants
# --- Your Requested Helper Methods ---
    def move_applicant_to_another_step(self, applicant_id, new_step, comment):
        """Invalidates current step and creates a new row for the new step"""
        applicant = self.getone("custom_applicants" ,filters={"job_applicant":applicant_id})
        if not applicant:
            raise Exception("applicant not exists on this job")
        applicant.set("invalidated_at" , now_datetime())
        applicant.set("invalidated_by" , frappe.session.user)
        new_record = {
            "job_applicant": applicant_id,
            "step": new_step,
            "applicant_resume": applicant.get("applicant_resume"),
            "comment": comment
        }
        self.append("custom_applicants", new_record)
