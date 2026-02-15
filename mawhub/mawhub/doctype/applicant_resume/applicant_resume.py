import json
from frappe.model.document import Document
from frappe.model.naming import make_autoname

from mawhub.pkg.objectutils.objectutils import pick_keys_from_rows


class ApplicantResume(Document):
    def autoname(self):
        self.name = make_autoname(f"{str(self.get("job_applicant")).replace('@' , '--')}-.####")
    # def before_save(self):
    #     """Build normalized resume JSON snapshot"""
    #     experience_keys = ["company", "title", "start_date", "end_date", "description", "idx"]
    #     education_keys = ["institution", "degree", "field", "start_date", "end_date", "idx"]
    #     projects_keys = ["name", "description", "technologies", "link", "idx"]
    #     links_keys = ["label", "url", "idx"]
    #     current_dict = self.as_dict()
    #     payload = {
    #         "summary": current_dict.get("summary"),
    #         "skills": current_dict.get("skills"),
    #         "raw_resume_text": current_dict.get("raw_resume_text"),
    #         "experience": pick_keys_from_rows(current_dict.get("experience") or [], experience_keys),
    #         "education": pick_keys_from_rows(current_dict.get("education") or [], education_keys),
    #         "projects": pick_keys_from_rows(current_dict.get("projects") or [], projects_keys),
    #         "links": pick_keys_from_rows(current_dict.get("links") or [], links_keys),
    #     }
    #     self.set("raw_resume_text", json.dumps(payload, default=str))
    #
    #
