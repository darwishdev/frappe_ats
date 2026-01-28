from typing import List, Protocol, cast
import frappe

from mawhub.app.job.dto.applicant_resume import ApplicantResumeDTO
from mawhub.pkg.baseclasses.app_repo import AppRepo, AppRepoInterface
from mawhub.sqltypes.table_models import JobOpening
from mawhub.sqltypes.tal_models import JobView
class JobOpeningRepoInterface(AppRepoInterface[JobOpening],Protocol):
	def job_opening_list(self, user_name: str)->List[JobView]: ...
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
            },
        )
    def job_opening_list(self,user_name:str)->List[JobView]:
        print(user_name)
        raw_rows = frappe.db.sql("""
        select * from tal_job_view ;
        """,as_dict=True)
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
