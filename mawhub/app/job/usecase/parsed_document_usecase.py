import hashlib
import json
from typing import   Iterator, List, Protocol, cast
from frappe import Callable, Optional
from frappe.model.document import Document
from mawhub.app.job.agent.document_parser_agent import  DocumentParserWorkflow
from mawhub.app.job.dto.parsed_document_dto import ParsedDocumentDTO, ParsedDocumentParseRequest, ParsedDocumentWithSections, parsed_document_agent_to_dto, parsed_document_dto_to_sql
from mawhub.app.job.repo.job_repo import JobRepoInterface
from mawhub.pkg.pdfconvertor.pdfconvertor import extract_text_from_pdf

class ParsedDocumentUsecaseInterface(Protocol):
	def parsed_document_create_update(self, payload: ParsedDocumentDTO)->Document: ...
	def parse_document(self, payload: ParsedDocumentParseRequest,on_final_event: Optional[Callable[[dict], None]] = None)->Iterator[str]: ...
	def parsed_document_bulk_create(
        self,
        payload:List[ParsedDocumentDTO],
    )->List[Document]: ...

class ParsedDocumentUsecase:
    repo: JobRepoInterface
    document_parser_agent: DocumentParserWorkflow
    def __init__(
        self,
        repo: JobRepoInterface,
        document_parser_agent: DocumentParserWorkflow
    ):
        self.repo = repo
        self.document_parser_agent = document_parser_agent

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
        payload: ParsedDocumentParseRequest,
        on_final_event: Optional[Callable[[dict], None]] = None
    ) -> Iterator[str]:
        try:
            path = payload.get("path" , "")
            document_text = extract_text_from_pdf(path)
            # 2. Iterate through the workflow events
            for event in self.document_parser_agent.run(document_text):
                # Convert Pydantic models/Dicts to JSON
                # Using default=str to handle any potential non-serializable objects
                json_data = json.dumps(event, default=str)

                # 3. Yield in SSE format: "data: <payload>\n\n"
                yield f"data: {json_data}\n\n"
                if event["event"] == "final":
                    clean_text = document_text.strip().encode('utf-8')
                    hash_text =  hashlib.sha256(clean_text).hexdigest()
                    dto = parsed_document_agent_to_dto(
                        event["data"],
                        path,
                        hash_text,
                        payload.get("parent_id" , ""),
                        payload.get("parent_type" , ""),
                    )
                    self.parsed_document_create_update(dto)
                    # Run the callback if provided
                    if on_final_event:
                        on_final_event(cast(dict,event["data"]))

        except Exception as e:
            error_payload = json.dumps({"event": "error", "data": {"message": str(e)}})
            yield f"data: {error_payload}\n\n"

