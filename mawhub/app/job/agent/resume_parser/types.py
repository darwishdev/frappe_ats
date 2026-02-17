from typing import  List, Literal,  Union
from pydantic import BaseModel, Field

# Import DTO types directly
from mawhub.app.job.dto.applicant_resume_dto import (
    PersonalInfo as DTOPersonalInfo,
    ApplicantExperience as DTOApplicantExperience,
    ApplicantProject as DTOApplicantProject,
    ApplicantEducation as DTOApplicantEducation
)

# --- 1. Models with 'Model' suffix ---

class ApplicantExperienceModel(BaseModel):
    company: str = Field(
        description="Company or organization name exactly as written in the resume. Do not normalize."
    )
    role: str = Field(
        description="Job title or role exactly as written. Do not merge multiple roles."
    )
    from_date: str = Field(
        description="Start date exactly as written (no normalization or inference)."
    )
    to_date: str = Field(
        description="End date exactly as written. If ongoing, return the literal text such as 'Present'."
    )
    responsibilities: str = Field(
        description="Responsibilities and achievements exactly as written. Preserve wording."
    )

class ApplicantEducationModel(BaseModel):
    institution: str = Field(
        description="Institution or university name exactly as written."
    )
    degree: str = Field(
        description="Degree or certification exactly as written. Do not infer level."
    )
    from_date: str = Field(
        description="Start date exactly as written."
    )
    to_date: str = Field(
        description="End or graduation date exactly as written."
    )

class ApplicantProjectModel(BaseModel):
    title: str = Field(
        description="Project name exactly as written."
    )
    description: str = Field(
        description="Project description exactly as written. Do not summarize."
    )
    stack: str = Field(
        description="Stack used inside the project"
    )
    link: str = Field(
        description="Project URL if present. Otherwise return empty string."
    )

class ExperienceListModel(BaseModel):
    items: List[ApplicantExperienceModel] = Field(
        description="List of distinct work experience roles. Do not merge roles."
    )

class ProjectListModel(BaseModel):
    items: List[ApplicantProjectModel] = Field(
        description="List of projects. Each item must represent one project only."
    )

class EducationListModel(BaseModel):
    items: List[ApplicantEducationModel] = Field(
        description="List of education records. One record per degree or program."
    )

class SkillListModel(BaseModel):
    items: List[str] = Field(description="A list of technical and soft skills extracted from the text")

SectionNames = Literal["personal", "summary", "skills", "experience", "projects", "education"]

class ResumeSectionModel(BaseModel):
    name: SectionNames = Field(
        description="One of exactly: personal, summary, skills, experience, projects, education"
    )
    content: str = Field(
        description="Original resume text belonging to this section only. Do not rewrite."
    )

class ChunkedResumeModel(BaseModel):
    sections: List[ResumeSectionModel] = Field(
        description="Resume text split into the predefined section names only."
    )

class PersonalInfoModel(BaseModel):
    name: str = Field(description="Full candidate name as written in the resume")
    email: str = Field(
        description="Email address from the resume. Return empty string if not found"
    )
    phone: str = Field(
        description="Phone number as written. Return empty string if missing"
    )
    location: str = Field(
        description="City/country or location text from the resume"
    )
    links: List[str] = Field(
        description="List of profile or portfolio URLs (LinkedIn, GitHub, website). Empty list if none"
    )

class SummaryModel(BaseModel):
    summary: str = Field(
        description="Summary of the profile"
    )

# --- 2. Type Aliases using DTO types ---

AgentSection = Union[
    PersonalInfoModel,
    SummaryModel,
    SkillListModel,
    ExperienceListModel,
    ProjectListModel,
    EducationListModel
]

AgentSectionDict = Union[
    DTOPersonalInfo,
    List[str],
    str,
    List[DTOApplicantExperience],
    List[DTOApplicantProject],
    List[DTOApplicantEducation]
]
