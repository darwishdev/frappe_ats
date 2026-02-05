from typing import Any, Dict, List, Protocol, cast
import frappe

from mawhub.app.job.dto.applicant_resume import ApplicantResumeDTO
from mawhub.pkg.baseclasses.app_repo import AppRepo, AppRepoInterface
from mawhub.sqltypes.table_models import JobOpening
from mawhub.sqltypes.tal_models import JobView
class JobOpeningRepoInterface(AppRepoInterface[JobOpening],Protocol):
    def job_opening_list(self,filters: Dict[str, Any] | None = None)->List[JobView]: ...
    def job_opening_find(self, job: str)->JobView: ...


class JobOpeningRepo(AppRepo[JobOpening]):
    def __init__(self):
        super().__init__(
            doc_name="Job Opening",
            name_key="name",
            scalar_fields=[
                "job_title",
                "status",
                "description",
                "department",
                "employment_type",
                "custom_customer",
                "location",
                "staffing_plan",
                "planned_vacancies",
                "publish",
                "publish_applications_received",
                "currency",
                "company",
                "designation",
                "lower_range",
                "upper_range",
                "salary_per",
                "publish_salary_range",
                "custom_pipeline",
            ],
            child_tables={
                "custom_pipeline_steps" : "custom_pipeline_steps",
            },
        )
    def job_opening_list(self,filters: Dict[str, Any] | None = None)->List[JobView]:
        raw_rows = frappe.db.sql("""
        select * from tal_job_view j
WHERE j.custom_customer = IF(LENGTH(%(customer)s) > 0  , %(customer)s, j.custom_customer)
AND j.owner = IF(LENGTH(%(owner)s) > 0  , %(owner)s, j.owner)
        """,filters,as_dict=True)
        if raw_rows is None:
            return cast(List[JobView] , [])

        if not isinstance(raw_rows,list):
            raise TypeError(
                f"Expected list from frappe.db.sql, got {type(raw_rows)}"
            )
        return cast(List[JobView] , raw_rows)

    def job_opening_find(self,job:str)->JobView:
        raw_rows = frappe.db.sql("""
        select * from tal_job_view where name = %s limit 1 ;
        """,(job,),as_dict=True)
        if raw_rows is None:
            raise frappe.NotFound(f"no job with id : {job}")

        if not isinstance(raw_rows,list):
            raise TypeError(
                f"Expected list from frappe.db.sql, got {type(raw_rows)}"
            )

        rows = cast(List[JobView] , raw_rows)
        return rows[0]
