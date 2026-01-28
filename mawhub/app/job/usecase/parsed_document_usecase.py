import json
from typing import  Iterator, List, Protocol

from frappe.model.document import Document
from frappe import _dict
from mawhub.app.job.agent.resume_parser_agent import AgentEvent, ResumeWorkflow
from mawhub.app.job.dto.parsed_document_dto import ParsedDocumentDTO, ParsedDocumentWithSections, parsed_document_dto_to_sql
from mawhub.app.job.repo.job_repo import JobRepoInterface

class ParsedDocumentUsecaseInterface(Protocol):
	def parsed_document_create_update(self, payload: ParsedDocumentDTO)->Document: ...
	def parsed_document_bulk_create(
        self,
        payload:List[ParsedDocumentDTO]
    )->List[Document]: ...

class ParsedDocumentUsecase:
    repo: JobRepoInterface
    resume_agent: ResumeWorkflow
    def __init__(
        self,
        repo: JobRepoInterface,
        resume_agent: ResumeWorkflow
    ):
        self.repo = repo
        self.resume_agent = resume_agent

    def parsed_document_create_update(self, payload: ParsedDocumentDTO)->Document:
        sql_params = parsed_document_dto_to_sql(payload)
        return self.repo.parsed_document.create_or_update(sql_params)


    def parsed_document_bulk_create(
        self,
        payload:List[ParsedDocumentDTO]
    )->List[Document]:
        p :List[ParsedDocumentWithSections]= []
        for doc in payload:
            sql_params = parsed_document_dto_to_sql(doc)
            p.append(sql_params)
        return self.repo.parsed_document.bulk_create(p)
