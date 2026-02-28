# from datetime import date, datetime
# from typing import Dict, List, TypedDict
# from frappe import Any, Optional
#
from typing import TypedDict

from frappe import Optional

from mawhub.agent.job_opening_parser.job_opening_parser_agent import JobOpeningEvent
from mawhub.app.job.repo.job_opening_repo import JobOpeningDBModel


class JobPipelineStepApplicantDTO(TypedDict):
    name: str
    job_applicant: str
    applicant_resume: str
    comment: str

class JobPipelineStepDTO(TypedDict):
    name: str
    step_code: str
    step_name: str
    step_type: str
    step_idx: int
    applicant_count: int
# class JobOpeningDTO(TypedDict):
#     name: str
#     designation: str
#     department: Optional[str]
#     pipeline: Optional[str]
#     parsed_documents:List[Any]
#     employment_type: str
#     location: str
#     customer: str
#     docstatus: int
#     publish: int
#     publish_salary_range: int
#     publish_applications_received: int
#     currency: str
#     salary_per: str
#     lower_range: str
#     upper_range: str
#     posted_on: str
#     closes_on: str
#     step_count: int
#     applicants_count: int
#     steps: List[JobPipelineStepDTO]
#     # the map key should be the step code
#     steps_map: Dict[str,List[JobPipelineStepApplicantDTO]]
#
#
# def _dt_to_str(value: date | datetime | None) -> str:
#     if value is None:
#         return ""
#     return value.isoformat()
#
#
# # T = TypeVar("T")
# #
# # def get(
# #     row: Mapping[str, Any],
# #     key: str,
# #     default: T,
# # ) -> T:
# #     value = row.get(key, default)
# #     return cast(T, value)
# # def job_opening_sql_to_dto(job: JobView) -> JobOpeningDTO:
# #     # ---------------------------
# #     # Parse steps
# #     # ---------------------------
# #     steps_raw = get(job, "steps", [])
# #     if isinstance(steps_raw, str):
# #         try:
# #             steps = json.loads(steps_raw)
# #         except json.JSONDecodeError as exc:
# #             raise ValueError("Invalid JSON in job.steps") from exc
# #     else:
# #         steps = []
# #
# #     steps = cast(list[JobPipelineStepDTO], steps)
# #
# #     all_steps = []
# #     for step in steps:
# #         for step_applicant in step["candidates"]:
# #             all_steps.append(step_applicant)
# #
# #     steps.insert(0,{
# #         "candidates" : all_steps,
# #         "step_id" : "All",
# #         "step_name" : "All",
# #         "step_type" : "All",
# #         "candidate_count" : len(all_steps),
# #         "step_idx" : 1
# #         })
# #     parsed_documents  : str = cast(str,get(job, "parsed_documents", "[]"))
# #     dto: JobOpeningDTO = {
# #         "name": get(job, "name", ""),
# #         "designation": get(job, "designation", ""),
# #         "department": get(job, "department", ""),
# #         "parsed_documents": json.loads(parsed_documents),
# #         "employment_type": get(job, "employment_type", ""),
# #         "location": get(job, "location", ""),
# #         "customer": get(job, "custom_customer", ""),
# #         "pipeline": get(job, "custom_pipeline", ""),
# #         "docstatus": get(job, "docstatus", 1),
# #         "publish": get(job, "publish", True),
# #         "publish_salary_range": get(job, "publish_salary_range", False),
# #         "publish_applications_received": get(job, "publish_applications_received", False),
# #
# #         "route": get(job, "route", ""),
# #         "job_application_route": get(job, "job_application_route", ""),
# #
# #         "currency": get(job, "currency", ""),
# #         "salary_per": get(job, "salary_per", ""),
# #         "lower_range": str(get(job, "lower_range", 0)),
# #         "upper_range": str(get(job, "upper_range", 0)),
# #
# #         "posted_on": _dt_to_str(job.get("posted_on")),
# #         "closes_on": _dt_to_str(job.get("closes_on")),
# #
# #         "step_count": get(job, "step_count", 0),
# #         "candidate_count": get(job, "candidate_count", 0),
# #
# #         "steps": steps,
# #     }
# #
# #     return dto
# #
# #
# # def job_opening_list_sql_to_dto(
# #     jobs: List[JobView] | None,
# # ) -> List[JobOpeningDTO]:
# #     """
# #     Convert a list of DB JobView rows into JobOpeningDTOs.
# #     """
# #     if not jobs:
# #         return []
# #
# #     result: List[JobOpeningDTO] = []
# #     for job in jobs:
# #         result.append(job_opening_sql_to_dto(job))
# #
# #     return result
# # class JobOpeningCreateRequest(TypedDict):
# #     job_title: str
# #     designation: NotRequired[str]
# #     company: NotRequired[str]
# #     location: NotRequired[str]
# #     planned_vacancies: int
# #     vacancies: int
# #     lower_range: float
# #     upper_range: float
# #     publish: int
# #     publish_salary_range: int
# #     publish_applications_received: int
# #     customer: int
def job_opening_create_request_from_agent(
        event: JobOpeningEvent,
        request_id: str,
        designation_id: Optional[str] = None,
        customer_id: Optional[str] = None,
        location_id: Optional[str] = None
    ) -> JobOpeningDBModel:
    """
    Adapts a JobOpeningEvent to a JobOpeningCreateRequest format.
    Maps 'customer' string to 'company' and initializes default publish flags.
    """
    # Initialize the request with direct mappings
    request: JobOpeningDBModel = {
        "job_title": event["job_title"],
        "designation": event["designation"] or event["job_title"] or "",
        "status":"Open",
        "custom_parse_request_id": request_id,
        "planned_vacancies": event["planned_vacancies"],
        "vacancies": event["vacancies"],
        "custom_parse_request_id": request_id,
        "lower_range": event["lower_range"],
        "upper_range": event["upper_range"],
        "salary_per": "Month",
        "company" : "Mawhub",
        # Default flags for the request (assuming 1 for True/Active)
        "publish": 1,
        "publish_salary_range": 1,
        "publish_applications_received": 1,
    }
    if designation_id:
        request["designation"] = designation_id

    if customer_id:
        request["custom_customer"] = customer_id

    if location_id:
        request["location"] = location_id
    return request
