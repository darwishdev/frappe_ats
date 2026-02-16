import hashlib
from typing import   Iterator, List, Protocol
import frappe
from frappe.model.document import Document
from mawhub.app.job.agent.document_parser_agent import  DocumentParserEvent, DocumentParserWorkflow, ParsedDocumentFinalEvent
from mawhub.app.job.agent.job_opening_parser_agent import JobOpeningParserWorkflow
from mawhub.app.job.dto.parsed_document_dto import ParsedDocumentDTO,   ParsedDocumentWithSections, parsed_document_agent_to_dto,  parsed_document_dto_to_sql
from mawhub.app.job.repo.job_repo import JobRepoInterface
from mawhub.pkg.sql.sql_utils import get_cached_output

class ParsedDocumentUsecaseInterface(Protocol):
	def parsed_document_create_update(self, payload: ParsedDocumentDTO)->Document: ...
	def parse_document(
            self,
            file_path:str,
            document_text:str,
            request_id:str
    )->Iterator[dict]: ...
	def parsed_document_bulk_create(
        self,
        payload:List[ParsedDocumentDTO],
    )->List[Document]: ...

class ParsedDocumentUsecase:
    repo: JobRepoInterface
    document_parser_agent: DocumentParserWorkflow
    job_opening_parser_agent: JobOpeningParserWorkflow
    def __init__(
        self,
        repo: JobRepoInterface,
        document_parser_agent: DocumentParserWorkflow,
        job_opening_parser_agent: JobOpeningParserWorkflow
    ):
        self.repo = repo
        self.document_parser_agent = document_parser_agent
        self.job_opening_parser_agent = job_opening_parser_agent

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

    def parse_document(
        self,
        file_path: str,
        document_text: str,
        request_id: str
    )->Iterator[dict]:
        def callback(final_event_data: ParsedDocumentFinalEvent):
            db_req = parsed_document_agent_to_dto(final_event_data,file_path,text_hash,request_id)
            try:
                parsed_doc = self.parsed_document_create_update(db_req)
                frappe.db.commit()
                return parsed_doc
            except Exception as e:
                raise Exception(f"failed writing the document to db : {e} : body: {db_req}")

        try:
            text_hash = hashlib.sha256(document_text.strip().encode("utf-8")).hexdigest()
            cache_result = get_cached_output(
                    doctype="Parsed Document",
                    key_field="name",
                    key_value=text_hash,
                    expected_type=ParsedDocumentFinalEvent,
                    output_field="output"
            )
            if cache_result:
                cache_name , cached_data = cache_result
                yield {
                    "event":"final" ,
                    "data": cached_data
                }
                doc = callback(cached_data)
                yield {
                    "event":"db_save" ,
                    "data": str(doc.name)
                }
                return

            for event in self.document_parser_agent.run(document_text):
                yield {"event" : event["event"] ,"data" : event["data"]}
                if event["event"] == "final":
                    final_event_data = event["data"]
                    doc = callback(final_event_data)
                    yield {
                        "event":"db_save" ,
                        "data": str(doc.name)
                    }
                    print(f"finalevent is {event['event']}")
        except Exception as e:
            yield {"event" : "error" , "data" : str(e)}

