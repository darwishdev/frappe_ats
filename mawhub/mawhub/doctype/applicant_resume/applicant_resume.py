import json
from frappe.model.document import Document
from frappe.model.naming import make_autoname

from mawhub.pkg.objectutils.objectutils import pick_keys_from_rows


class ApplicantResume(Document):
    def autoname(self):
        self.name = make_autoname(f"{str(self.get("job_applicant")).replace('@' , '--')}-.####")
    def before_save(self):
        """Build normalized resume JSON snapshot"""
        experience_keys = ["company", "title", "start_date", "end_date", "description", "idx"]
        education_keys = ["institution", "degree", "field", "start_date", "end_date", "idx"]
        projects_keys = ["name", "description", "technologies", "link", "idx"]
        links_keys = ["label", "url", "idx"]
        payload = {
            "summary": self.get("summary"),
            "skills": self.get("skills"),
            "raw_resume_text": self.get("raw_resume_text"),
            "experience": pick_keys_from_rows(self.get("experience") or [], experience_keys),
            "education": pick_keys_from_rows(self.get("education") or [], education_keys),
            "projects": pick_keys_from_rows(self.get("projects") or [], projects_keys),
            "links": pick_keys_from_rows(self.get("links") or [], links_keys),
        }
        self.set("output", json.dumps(payload, ensure_ascii=False))


