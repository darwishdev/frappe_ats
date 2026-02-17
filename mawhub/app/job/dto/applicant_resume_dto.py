from typing import List, NotRequired, Required, TypedDict

# from mawhub.app.job.agent.resume_parser_agent import AgentFinalEvent
#
class PersonalInfo(TypedDict, total=False):
    email: Required[str]
    name: str
    phone: str
    location: str
#
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
    stack: str
    link: str




class ApplicantResumeDTO(TypedDict, total=False):
    resume_hash: Required[str]
    applicant_name: Required[str]
    email: Required[str]
    phone: NotRequired[str]
    file_path: Required[str]
    location: NotRequired[str]
    skills: NotRequired[str]
    summary: NotRequired[str]
    experience: NotRequired[List[ApplicantExperience]]
    education: NotRequired[List[ApplicantEducation]]
    projects: NotRequired[List[ApplicantProject]]

