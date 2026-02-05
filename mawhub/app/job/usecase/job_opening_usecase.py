from annotated_types import LowerCase
from frappe import Any, LinkValidationError, _
from typing import  Dict, List, Protocol

import frappe
from frappe.model.document import Document
from mawhub.app.job.agent.document_parser_agent import DocumentParserWorkflow
from mawhub.app.job.agent.job_opening_parser_agent import  JobOpeningParserWorkflow
from mawhub.app.job.dto.job_opening import JobOpeningDTO, job_opening_list_sql_to_dto, job_opening_sql_to_dto
from mawhub.app.job.repo.job_repo import  JobRepoInterface
from mawhub.pkg.pdfconvertor.pdfconvertor import extract_text_from_pdf
from mawhub.sqltypes.table_models import JobOpening


class JobOpeningUsecaseInterface(Protocol):
    def job_opening_list(
        self,
        filters: Dict[str,Any],
    ) -> List[JobOpeningDTO]: ...
    def job_opening_create_update(
        self,
        payload: JobOpening,
    ) -> Document: ...
    # def job_opening_parse(
    #     self,
    #     path: str,
    # ) -> Iterator[JobAgentEvent]: ...
    def job_opening_find(
        self,
        job: str,
    ) -> JobOpeningDTO: ...
class JobOpeningUsecase:
    repo: JobRepoInterface
    job_agent: JobOpeningParserWorkflow
    document_parser_agent: DocumentParserWorkflow
    def __init__(
        self,
        repo: JobRepoInterface,
        job_agent: JobOpeningParserWorkflow,
        document_parser_agent: DocumentParserWorkflow,
    ):
        self.repo = repo
        self.job_agent = job_agent
        self.document_parser_agent = document_parser_agent

    def job_opening_list(
        self,
        filters: Dict[str,Any],
    ) -> List[JobOpeningDTO]:
        db_rows = self.repo.job_opening.job_opening_list(filters)
        return job_opening_list_sql_to_dto(db_rows)


    def job_opening_create_update(
        self,
        payload: JobOpening,
    ) -> Document:
        """
        Create or update a JobOpening.
        If a LinkValidationError occurs due to missing Location,
        create the Location and retry.
        """
        try:
            designation = frappe.get_doc("Designation" , payload.get("designation" , ""))
            if not designation:
                try:
                    frappe.get_doc({
                        "doctype": "Designation",
                        "designation_name": payload.get("designation" , "")
                    }).insert(ignore_permissions=True)
                    frappe.db.commit()  # commit so it exists before retry
                except Exception as designation_error:
                    frappe.log_error(
                        f"Failed to create missing designation '{payload.get("location")}': {designation_error}",
                        "job_opening_create_update"
                    )
                    raise designation_error  # re-raise if we cannot create
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

    def job_opening_find(
        self,
        job: str,
    ) -> JobOpeningDTO:
        db_rows = self.repo.job_opening.job_opening_find(job)
        return job_opening_sql_to_dto(db_rows)

