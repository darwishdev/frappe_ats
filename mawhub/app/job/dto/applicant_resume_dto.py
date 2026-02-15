from typing import List, NotRequired, Required, TypedDict

# from mawhub.app.job.agent.resume_parser_agent import AgentFinalEvent

class PersonalInfo(TypedDict, total=False):
    name: str
    email: Required[str]
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




class ApplicantResumeDTO(TypedDict, total=False):
    job_applicant: Required[str]
    request_id: Required[str]
    file_path: Required[str]
    personal: Required[PersonalInfo]
    skills: NotRequired[str]
    summary: NotRequired[str]
    raw_resume_text: NotRequired[str]
    resume_hash: NotRequired[str]
    experience: NotRequired[List[ApplicantExperience]]
    education: NotRequired[List[ApplicantEducation]]
    projects: NotRequired[List[ApplicantProject]]

