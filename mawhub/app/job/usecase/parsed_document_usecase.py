import hashlib
from typing import   Iterator, List, Protocol
import frappe
from frappe.model.document import Document
from mawhub.app.job.agent.document_parser.document_parser_agent import  DocumentParserWorkflow
from mawhub.app.job.repo.job_repo import JobRepoInterface
from mawhub.mawhub.doctype.parsed_document.parsed_document import ParsedDocumentDBModel
from mawhub.pkg.sql.sql_utils import get_cached_output

class ParsedDocumentUsecaseInterface(Protocol):
	def parsed_document_create_update(self, payload: ParsedDocumentDBModel)->Document: ...
	def parse_document(
            self,
            file_path:str,
            document_text:str,
            request_id:str,
    )->Iterator[dict]: ...
	def parsed_document_bulk_create(
        self,
        payload:List[ParsedDocumentDBModel],
    )->List[Document]: ...

class ParsedDocumentUsecase:
    repo: JobRepoInterface
    document_parser_agent: DocumentParserWorkflow
    def __init__(
        self,
        repo: JobRepoInterface,
        document_parser_agent: DocumentParserWorkflow,
    ):
        self.repo = repo
        self.document_parser_agent = document_parser_agent

    def parsed_document_create_update(self, payload: ParsedDocumentDBModel)->Document:
        return self.repo.parsed_document.create_or_update(payload)


    def parsed_document_bulk_create(
        self,
        payload:List[ParsedDocumentDBModel]
    )->List[Document]:
        p :List[ParsedDocumentDBModel]= []
        for doc in payload:
            p.append(doc)
        return self.repo.parsed_document.bulk_create(p)

    def parse_document(
        self,
        file_path: str,
        document_text: str,
        request_id: str,
    )->Iterator[dict]:
        def callback(final_event_data: ParsedDocumentDBModel):
            # db_req = parsed_document_agent_to_dto(final_event_data,file_path,text_hash,request_id)
            try:
                text_hash = hashlib.sha256(document_text.strip().encode("utf-8")).hexdigest()
                final_event_data["request_id"] = request_id
                final_event_data["file_hash"] = text_hash
                final_event_data["file_path"] = file_path
                parsed_doc = self.parsed_document_create_update(final_event_data)
                frappe.db.commit()
                return parsed_doc
            except Exception as e:
                raise Exception(f"failed writing the document to db : {e} : body: {final_event_data}")

        try:
            text_hash = hashlib.sha256(document_text.strip().encode("utf-8")).hexdigest()
            cache_name , cached_data = get_cached_output(
                    doctype="Parsed Document",
                    key_field="name",
                    key_value=text_hash,
                    expected_type=ParsedDocumentDBModel,
            )
            if cache_name and cached_data:
                yield {
                    "event":"final" ,
                    "data": cached_data
                }
                try:
                    doc = callback(cached_data)
                    yield {
                        "event":"db_save" ,
                        "data": str(doc.name)
                    }
                    return
                except Exception as e:
                    yield {
                            "event" : "error",
                            "data" : str(e)
                            }
                    raise e


            for event in self.document_parser_agent.run(document_text):
                print(f"events is {event}")
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

