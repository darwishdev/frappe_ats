from typing import List, Literal, NotRequired, Protocol, TypedDict
import frappe

from mawhub.pkg.baseclasses.app_repo import AppRepo, AppRepoInterface
# from mawhub.sqltypes.table_models import JobApplicant


class JobApplicantDBModel(TypedDict):
    name: NotRequired[str]
    # -------------------------
    # core fields
    # -------------------------
    applicant_name: str
    email_id: str

    status: Literal[
        "Open",
        "Replied",
        "Rejected",
        "Hold",
        "Accepted",
    ]

    phone_number: NotRequired[str]
    country: NotRequired[str]

    # -------------------------
    # job link
    # -------------------------
    job_title: NotRequired[str]          # Link -> Job Opening
    designation: NotRequired[str]        # Link -> Designation

    # -------------------------
    # source fields
    # -------------------------
    source: NotRequired[str]             # Link -> Job Applicant Source
    source_name: NotRequired[str]        # Link -> Employee
    employee_referral: NotRequired[str]  # Link -> Employee Referral

    applicant_rating: float | None

    # -------------------------
    # resume fields
    # -------------------------
    cover_letter: NotRequired[str]       # Text
    resume_attachment: NotRequired[str]  # Attach
    resume_link: NotRequired[str]
    notes: NotRequired[str]

    # -------------------------
    # salary expectation
    # -------------------------
    currency: NotRequired[str]
    lower_range: float | None
    upper_range: float | None
class JobApplicantRepoInterface(AppRepoInterface[JobApplicantDBModel] , Protocol):
    def job_applicant_find(self, name: str,job: str)->dict: ...


class JobApplicantRepo(AppRepo[JobApplicantDBModel]):
    def __init__(self):
        super().__init__(
            doc_name="Job Applicant",
            name_key="name",
            scalar_fields=[
                "name",

                "applicant_name",
                "email_id",
                "status",
                "phone_number",
                "country",

                "job_title",
                "designation",

                "source",
                "source_name",
                "employee_referral",
                "applicant_rating",

                "cover_letter",
                "resume_attachment",
                "resume_link",
                "notes",

                "currency",
                "lower_range",
                "upper_range"
            ],
            child_tables={
            },
        )


    def job_applicant_find(self, name: str,job: str)->dict:
        applicant_doc = frappe.get_doc("Job Applicant" , name)
        interviews = frappe.get_all(
                "Interview" ,
                filters={"job_applicant" : name} ,
                fields=[
                    "name",
                    "creation",
                    "modified",
                    "modified_by",
                    "owner",
                    "docstatus",
                    "interview_round",
                    "job_applicant",
                    "job_opening",
                    "designation",
                    "resume_link",
                    "status",
                    "scheduled_on",
                    "from_time",
                    "to_time",
                    "expected_average_rating",
                    "average_rating",
                    "interview_summary",
                    "reminded",
                    "amended_from"
                    ]
                )
        response = {
                "applicant" : applicant_doc.as_dict(),
                "interviews" : interviews,
                }

        applicant_resume = frappe.db.sql("""
                                select a.applicant_resume from `tabJob Opening Applicant` a
                                where a.parent = %(job)s
                                AND a.parenttype = 'Job Opening'
                                AND a.job_applicant = %(applicant)s
                                AND a.invalidated_at IS NULL
                                LIMIT 1
                                """ , {"job" : job , "applicant" : name} , pluck=True)
        if not applicant_resume:
            print(f"""can't find the active resume for this candidate : {name} on this
                                         job : {job}""")
            return response
        if not isinstance(applicant_resume , list):
            return response
        if len(applicant_resume) == 0:
            return response
        applicant_resume = applicant_resume[0]
        resume_doc = frappe.get_doc("Applicant Resume" , str(applicant_resume))
        return {
            "applicant" : applicant_doc.as_dict(),
            "resume" : resume_doc.as_dict(),
            "interviews" : interviews,
        }

