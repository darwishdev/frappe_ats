from typing import List, Protocol, cast
import frappe

from mawhub.sqltypes.tal_models import JobView
class JobOpeningRepoInterface(Protocol):
	def job_opening_list(self, user_name: str)->List[JobView]: ...


class JobOpeningRepo:
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
        select * from tal_job_view where name = %s limit = 1 ;
        """,(job,),as_dict=True)
        if raw_rows is None:
            raise frappe.NotFound(f"no job with id : {job}")

        if not isinstance(raw_rows,list):
            raise TypeError(
                f"Expected list from frappe.db.sql, got {type(raw_rows)}"
            )

        rows = cast(List[JobView] , raw_rows)
        return rows[0]
