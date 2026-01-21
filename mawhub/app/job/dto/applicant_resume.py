from typing import List, NotRequired, TypedDict

class PersonalInfo(TypedDict, total=False):
    name: str
    email: str
    phone: str
    location: str
    links: List[str]

class ApplicantExperience(TypedDict, total=False):
    company: str
    role: str
    from_date: str
    to_date: str
    description: str


class ApplicantEducation(TypedDict, total=False):
    institution: str
    degree: str
    from_date: str
    to_date: str


class ApplicantProject(TypedDict, total=False):
    title: str
    description: str
    link: str


class ApplicantLink(TypedDict, total=False):
    label: str
    url: str


class ApplicantResumeDTO(TypedDict, total=False):
    job_applicant: str
    personal_info: PersonalInfo
    skills: NotRequired[str]
    summary: NotRequired[str]
    raw_resume_text: NotRequired[str]
    raw_resume_json: NotRequired[str]
    experience: NotRequired[List[ApplicantExperience]]
    education: NotRequired[List[ApplicantEducation]]
    projects: NotRequired[List[ApplicantProject]]
    links: NotRequired[List[ApplicantLink]]

