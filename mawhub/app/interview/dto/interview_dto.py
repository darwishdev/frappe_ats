from typing import  Required, TypedDict

from mawhub.mawhub.doctype.applicant_education.applicant_education import ApplicantEducationDBModel
from mawhub.mawhub.doctype.applicant_experience.applicant_experience import ApplicantExperienceDBModel
from mawhub.mawhub.doctype.applicant_project.applicant_project import ApplicantProjectDBModel
from mawhub.mawhub.doctype.applicant_resume.applicant_resume import ApplicantResumeDBModel

class PersonalInfo(TypedDict, total=False):
    email: Required[str]
    name: str
    phone: str
    location: str
#
class ApplicantExperience(ApplicantExperienceDBModel, total=False):
    pass


class ApplicantEducation(ApplicantEducationDBModel, total=False):
    pass


class ApplicantProject(ApplicantProjectDBModel, total=False):
    pass




class ApplicantResumeDTO(ApplicantResumeDBModel, total=False):
    pass
