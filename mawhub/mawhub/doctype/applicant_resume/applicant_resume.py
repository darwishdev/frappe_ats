from frappe.model.document import Document
from frappe.model.naming import make_autoname

from typing import NotRequired, TypedDict, List

from mawhub.mawhub.doctype.applicant_education.applicant_education import ApplicantEducationDBModel
from mawhub.mawhub.doctype.applicant_experience.applicant_experience import ApplicantExperienceDBModel
from mawhub.mawhub.doctype.applicant_project.applicant_project import ApplicantProjectDBModel


class ApplicantResumeDBModel(TypedDict):
    # -------------------------
    # frappe system fields
    # -------------------------
    name: NotRequired[str]
    idx: NotRequired[int]
    # -------------------------
    # scalar fields
    # -------------------------
    file_hash: str
    email: str
    phone: NotRequired[str]
    location: NotRequired[str]

    file_path: str
    links: NotRequired[str]

    summary: NotRequired[str]
    skills: NotRequired[str]

    # -------------------------
    # child tables
    # -------------------------
    experience: List[ApplicantExperienceDBModel]
    education: List[ApplicantEducationDBModel]
    projects: List[ApplicantProjectDBModel]

class ApplicantResume(Document):
    def autoname(self):
        self.name = make_autoname(f"{str(self.get("email")).replace('@' , '--')}-.####")
