import json
from frappe import Any, LinkValidationError, Optional,  _
from typing import  Dict, List, Protocol, cast

import frappe
from frappe.model.document import Document
from mawhub.app.job.agent.job_opening_parser.job_opening_parser_agent import  JobOpeningEvent, JobOpeningParserWorkflow
# from mawhub.app.job.dto.job_opening_dto import JobOpeningDTO, job_opening_create_request_from_agent, job_opening_list_sql_to_dto, job_opening_sql_to_dto
from mawhub.app.job.dto.job_opening_dto import job_opening_create_request_from_agent
from mawhub.app.job.repo.job_opening_repo import JobOpeningDBModel
from mawhub.app.job.repo.job_repo import  JobRepoInterface


class JobOpeningUsecaseInterface(Protocol):
    def job_opening_step_list(
            self,
            job_names:Optional[str],
            )-> Any: ...
    def job_opening_create_update(
        self,
        payload: JobOpeningDBModel,
    ) -> Document: ...
    def job_opening_parse(
        self,
        document_text: str,
        user:str,
        request_id:str
    ) -> JobOpeningEvent: ...

class JobOpeningUsecase:
    repo: JobRepoInterface
    job_agent: JobOpeningParserWorkflow
    def __init__(
        self,
        repo: JobRepoInterface,
        job_agent: JobOpeningParserWorkflow,
    ):
        self.repo = repo
        self.job_agent = job_agent

    def ensure_designation(self, designation_name: str) -> str:
        """Finds or creates Designation based on 'designation_name'."""
        # Filter matches the insert field
        exists = frappe.db.exists("Designation", {"designation_name": designation_name})
        if isinstance(exists,str):
            return exists

        doc = frappe.get_doc({
            "doctype": "Designation",
            "designation_name": designation_name
        }).insert(ignore_permissions=True)

        return str(doc.name)

    def ensure_customer(self, customer_name: str) -> str:
        """Finds or creates Customer based on 'customer_name'."""
        # Filter matches the insert field
        exists = frappe.db.exists("Customer", {"customer_name": customer_name})
        if isinstance(exists,str):
            return exists

        doc = frappe.get_doc({
            "doctype": "Customer",
            "customer_name": customer_name
        }).insert(ignore_permissions=True)

        return str(doc.name)

    def ensure_location(self, location_name: str) -> str:
        """Finds or creates Branch based on 'branch' field."""
        # Filter matches the 'branch' field as used in your insert logic
        exists = frappe.db.exists("Branch", {"branch": location_name})
        if isinstance(exists,str):
            return exists

        doc = frappe.get_doc({
            "doctype": "Branch",
            "branch": location_name
        }).insert(ignore_permissions=True)

        return str(doc.name)
    def job_opening_parse(
        self,
        document_text: str,
        user:str,
        request_id: str,
    ) -> JobOpeningEvent:
        response = self.job_agent.run(document_text)
        frappe.publish_realtime(
            event=f"job_parser",
            message={
               "job_title": response.get("job_title"),
               "designation": response.get("designation"),
               "customer": response.get("customer"),
               "location": response.get("location"),
               "planned_vacancies": response.get("planned_vacancies"),
               "vacancies": response.get("planned_vacancies"),
               "lower_range": response.get("lower_range"),
               "upper_range": response.get("upper_range")
                },
            user=user
        )
        designation_name = None
        if response.get("designation"):
            designation_name = self.ensure_designation(str(response["designation"]))
        else:
            designation_name = self.ensure_designation(str(response["job_title"]))
        customer_name = None
        if response.get("customer"):
            customer_name = self.ensure_customer(str(response["customer"]))

        location_name  = None
        if response.get("location"):
            location_name = self.ensure_location(str(response["location"]))
        db_create_req = job_opening_create_request_from_agent(
                response,
                designation_id=designation_name,
                customer_id=customer_name,
                request_id=request_id,
                location_id=location_name
        )
        job = self.job_opening_create_update(db_create_req)
        frappe.publish_realtime(
            event=f"job_parser",
            message={
               "name": job.name,
                },
            user=user
        )

        return response



    def job_opening_create_update(
        self,
        payload: JobOpeningDBModel,
    ) -> Document:
        """
        Create or update a JobOpening.
        If a LinkValidationError occurs due to missing Location,
        create the Location and retry.
        """
        try:
            payload["company"] = "Mawhub"
            designation_name = payload.get("designation", "")
            steps = payload.get("custom_pipeline_steps" , [])
            pipeline = payload.get("custom_pipeline")
            name = payload.get("name" , "")
            if len(steps) == 0 and len(name) == 0 and pipeline:
                steps_docs = frappe.get_all(
                        "Pipeline Step" ,
                        filters={"parent" : pipeline},
                        fields=[
                            "step_code",
                            "step_name",
                            "step_type"
                            ]
                )
                payload["custom_pipeline_steps"] = steps_docs
            if designation_name and not frappe.db.exists("Designation", designation_name):
                try:
                    frappe.get_doc({
                        "doctype": "Designation",
                        "designation_name": designation_name
                    }).insert(ignore_permissions=True)
                    frappe.db.commit()  # commit so it exists before retry
                except Exception as designation_error:
                    frappe.log_error(
                        f"Failed to create missing designation '{designation_name}': {designation_error}",
                        "job_opening_create_update"
                    )
                    raise
            return self.repo.job_opening.create_or_update(payload)

        except LinkValidationError as e:
            # Check if it's a missing Location error
            if "Location" in str(e):
                missing_location = payload.get("location")
                if missing_location:
                    # Create the Location dynamically
                    try:
                        frappe.get_doc({
                            "doctype": "Branch",
                            "branch": missing_location
                        }).insert(ignore_permissions=True)
                        frappe.db.commit()  # commit so it exists before retry
                    except Exception as inner_exc:
                        frappe.log_error(
                            f"Failed to create missing Location '{missing_location}': {inner_exc}",
                            "job_opening_create_update"
                        )
                        raise inner_exc  # re-raise if we cannot create

                    # Retry creating the job opening
                    return self.repo.job_opening.create_or_update(payload)

            if "Customer" in str(e):
                missing_customer = payload.get("custom_customer")
                if missing_customer:
                    try:
                        frappe.get_doc({
                            "doctype": "Customer",
                            "customer_name": missing_customer
                        }).insert(ignore_permissions=True)
                        frappe.db.commit()  # commit so it exists before retry
                    except Exception as inner_exc:
                        frappe.log_error(
                            f"Failed to create missing Location '{missing_customer}': {inner_exc}",
                            "job_opening_create_update"
                        )
                        raise inner_exc  # re-raise if we cannot create

                    # Retry creating the job opening
                    return self.repo.job_opening.create_or_update(payload)
            # If it's a different LinkValidationError, just raise
            raise ValueError(f"{str(e)}")

    def job_opening_step_list(
            self,
            job_names: Optional[str],
            )-> Any:
        resp = frappe.db.sql("""
                SELECT get_job_opening_step_stats(%s) job
                """,
                (job_names,),
                pluck=True)
        if not resp or not isinstance(resp,list):
            print(f"response is not list : {resp}")
            return None
        resp_row = resp[0]
        if not resp_row or not isinstance(resp_row,str):
            print(f"record is not string : {resp_row}")
            return None
        parsed = json.loads(resp_row)
        return  parsed
