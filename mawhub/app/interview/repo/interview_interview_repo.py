from concurrent.futures import ThreadPoolExecutor
import frappe
from mawhub.pkg.baseclasses.app_repo import AppRepo
from typing import  Literal, NotRequired, Protocol, TypedDict, cast
from mawhub.pkg.baseclasses.app_repo import AppRepo, AppRepoInterface
from mawhub.pkg.overrides.job_opening import CustomJobOpening


class InterviewDBModel(TypedDict):
    name: NotRequired[str]

    # -------------------------
    # core interview fields
    # -------------------------
    interview_round: str
    job_applicant: str

    status: Literal[
        "Pending",
        "Under Review",
        "Cleared",
        "Rejected",
        "Cancelled",
    ]

    scheduled_on: str
    from_time: str
    to_time: str

    # -------------------------
    # ratings
    # -------------------------
    average_rating: float | None
    expected_average_rating: float | None

    # -------------------------
    # additional info
    # -------------------------
    interview_summary: NotRequired[str]
    resume_link: NotRequired[str]

    # -------------------------
    # derived / fetched fields
    # -------------------------
    job_opening: NotRequired[str]
    designation: NotRequired[str]

    # -------------------------
    # flags
    # -------------------------
    reminded: NotRequired[int]
    amended_from: NotRequired[str]
class InterviewInterviewRepoInterface(AppRepoInterface[InterviewDBModel],Protocol):
    def interview_find(self, name: str) -> dict:...




class InterviewInterviewRepo(AppRepo[InterviewDBModel]):
    def __init__(self):
        super().__init__(
            doc_name="Interview",
            name_key="name",
            scalar_fields=[
                "name",

                # core
                "interview_round",
                "job_applicant",
                "status",
                "scheduled_on",
                "from_time",
                "to_time",

                # ratings
                "average_rating",
                "expected_average_rating",

                # info
                "interview_summary",
                "resume_link",

                # derived
                "job_opening",
                "designation",

                # flags
                "reminded",
                "amended_from",
            ],
            child_tables={
                # optional if you later want interviewers
                # "interview_details": "Interview Detail"
            },
        )
    def interview_round_find(self,name : str):
        round = frappe.get_doc("Interview Round" , name)
        if not round:
            return {}
        response = {"interview_round" : round.as_dict()}
        interview_type_name = round.get("interview_type" , "")
        if not isinstance(interview_type_name,str):
            return {}
        interview_type_doc = frappe.get_doc("Interview Type" , interview_type_name)
        if interview_type_doc:
            response["interview_type"] = interview_type_doc.as_dict()
        return response

    def interview_find(self, name: str) -> dict:
        interview = frappe.get_doc("Interview", name)
        if not interview:
            return {}
        applicant_name = str(interview.get("job_applicant" , ""))
        job_name = str(interview.get("custom_job_opening" , ""))
        interview_round = str(interview.get("interview_round" , ""))
        site = frappe.local.site
        def run_in_frappe_context(fn, *args, **kwargs):
            import frappe
            try:
                frappe.init(site=site)
                frappe.connect()
                return fn(*args, **kwargs)
            finally:
                frappe.destroy()
        def get_applicant_info(name : str):
            applicant = frappe.get_doc("Job Applicant" , name)
            if not applicant:
                return {"applicant" :{} }
            return {"applicant" : applicant.as_dict()}

        def get_job_info(job:str,applicant_id:str):
            job_opening = frappe.get_doc("Job Opening" , job)
            if not job_opening:
                return {}
            job_opening = cast(CustomJobOpening,job_opening)
            response = job_opening.job_find_by_applicant(applicant_id)
            return response

        with ThreadPoolExecutor(max_workers=3) as executor:
            future_applicant = executor.submit(
                run_in_frappe_context, get_applicant_info, applicant_name
            )
            future_job = executor.submit(
                run_in_frappe_context, get_job_info, job_name, applicant_name
            )
            future_round = executor.submit(
                run_in_frappe_context, self.interview_round_find, interview_round
            )

            applicant = future_applicant.result()
            job = future_job.result()
            round = future_round.result()
        return {
            "interview" : interview,
            **applicant,
            **job,
            **round,
        }
