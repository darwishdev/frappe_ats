
import json
from mawhub.agent.document_parser.instructions import VALIDATOR_SYSTEM_INSTRUCTION , CUNKER_SYSTEM_INSTRUCTION, EXTRACTOR_SYSTEM_INSTRUCTION
from frappe import Union
from typing import List, Literal, TypedDict
from google import genai
from google.genai import types
from typing import Dict, Iterator, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import cast

from mawhub.agent.document_parser.types import DocumentStructureModel, ParsedSectionModel, ValidationRequestModel, ValidationResponseModel
from mawhub.app.job.dto.parsed_document_dto import ParsedDocumentDTO, ParsedDocumentSectionDTO
from mawhub.mawhub.doctype.parsed_document_section.parsed_document_section import ParsedDocumentSectionDBModel
from mawhub.pkg.pdfconvertor.pdfconvertor import read_pdf_bytes

class DocumentStructureEvent(TypedDict):
    metadata: Dict[str,str]
    parsed_sections: Dict[str,str]
class DocumentAnalyzedEvent(TypedDict):
    event: Literal["analyzed"]
    data: DocumentStructureEvent

# 2️⃣ Section parsed
class SectionParsedEvent(TypedDict):
    event: Literal["section_parsed"]
    data: ParsedDocumentSectionDTO

# 3️⃣ Workflow finished
class WorkflowFinalEvent(TypedDict):
    event: Literal["final"]
    data: ParsedDocumentDTO

# 4️⃣ Error
class WorkflowErrorEvent(TypedDict):
    event: Literal["error"]
    data: str
class ValidationAcceptedEvent(TypedDict):
    event: Literal["validation_accepted"]
    data: None

class ValidationCorrectedEvent(TypedDict):
    event: Literal["validation_corrected"]
    data: ParsedDocumentDTO

DocumentParserEvent = Union[
    DocumentAnalyzedEvent,
    SectionParsedEvent,
    WorkflowFinalEvent,
    WorkflowErrorEvent,
    ValidationAcceptedEvent,
    ValidationCorrectedEvent,

]
# ----------------------------
# Workflow
# ----------------------------
class DocumentParserWorkflow:
    def __init__(
        self,
        client: genai.Client,
        model_name: str,
        get_cache_fn: Optional[Callable[[str, str], Optional[str]]] = None,
        set_cache_fn: Optional[Callable[[str, str, dict], None]] = None
    ):
        self.client = client
        self.default_model = model_name
        self.get_cache_fn = get_cache_fn
        self.set_cache_fn = set_cache_fn

    # Adapters (Convert Models to TypedDicts)
    # ----------------------------

    def _to_analyzed_event_data(self, doc_chunks: DocumentStructureModel) -> DocumentStructureEvent:
        """Adapts Pydantic DocumentStructure to simplified TypedDict"""
        return {
            "metadata": {
                item.key: item.value for item in doc_chunks.metadata
            },
            "parsed_sections": {
                section.title: section.text for section in doc_chunks.sections
            }
        }
    def _to_section_event_data(self, section_name: str, section: ParsedSectionModel) -> ParsedDocumentSectionDTO:
        """Adapts Pydantic ParsedSection to TypedDict ParsedSectionEvent"""
        print("section_nameisss" , section_name , section)
        data: ParsedDocumentSectionDTO = {
            "title": section_name,
        }

        if getattr(section, "description", None):
            data["description"] = section.description or ""

        if getattr(section, "footer", None):
            data["footer"] = section.footer or ""

        if getattr(section, "is_number_list", None) is not None:
            data["is_number_list"] = section.is_number_list

        if getattr(section, "bullet_points", None):
            # join bullet points if they exist
            data["bullet_points"] = "\n".join(str(x) for x in section.bullet_points or [])
        return data




    def _to_parsed_document_dto(
        self,
        validation_result: ValidationResponseModel,
        file_path: str,
    ) -> ParsedDocumentDTO:
        """
        Adapts ValidationResponseModel to ParsedDocumentDTO
        """
        # Use provided metadata or fallback to empty dict
        doc_metadata = getattr(validation_result,"metadata")

        # Convert each section in validation_result to ParsedDocumentSectionDTO
        sections: List[ParsedDocumentSectionDTO] = []
        for section in getattr(validation_result, "sections", []):
            section_dto: ParsedDocumentSectionDTO = {
                "title": getattr(section, "title", ""),
                "description": getattr(section, "description", ""),
                "footer": getattr(section, "footer", ""),
                "is_number_list": getattr(section, "is_number_list", False),
                "bullet_points": "\n".join(str(x) for x in getattr(section, "bullet_points", []) or [])
            }
            sections.append(section_dto)

        return ParsedDocumentDTO(
            request_id=getattr(validation_result, "request_id", ""),
            file_path=file_path,
            file_hash="",
            metadata=doc_metadata,
            sections=sections
        )
    def validate_document(
        self,
        full_text: str,
        metadata: dict,
        sections: List[ParsedDocumentSectionDTO],
        file_path: str,
        model_name: Optional[str] = None
    ) -> ValidationResponseModel:

        # Convert structured request to JSON

        request_payload = {
            "full_text": full_text,
            "file_path": file_path,
            "metadata": metadata,
            "sections": sections
        }

        # Build content parts
        request_json = json.dumps(request_payload, indent=2)
        parts = [
            types.Part.from_text(
                text="Validation Request JSON:\n" + request_json
            )
        ]

        pdf_bytes = read_pdf_bytes(file_path)
        # If file path provided → attach file
        if pdf_bytes:
            parts.append(
                types.Part.from_bytes(
                    data=pdf_bytes,
                    mime_type="application/pdf",
                )
            )
        response = self.client.models.generate_content(
            model=model_name or self.default_model,
            contents=types.Content(
                role="user",
                parts=parts
            ),
            config=types.GenerateContentConfig(
                system_instruction=VALIDATOR_SYSTEM_INSTRUCTION,
                temperature=0.0,
                response_mime_type="application/json",
                response_schema=ValidationResponseModel,
                max_output_tokens=4096,
                seed=42
            )
        )

        return cast(ValidationResponseModel,response.parsed)

    def chunk_document(self, text: str, model_name: str) -> DocumentStructureModel:
        prompt = f"""
            Parsed Document Text:
            {text}
        """
        response = self.client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=CUNKER_SYSTEM_INSTRUCTION,
                response_mime_type="application/json",
                response_schema=DocumentStructureModel
            )
        )
        return cast(DocumentStructureModel, response.parsed)

    def parse_section(self, text: str, model_name: str) -> ParsedSectionModel:
        prompt = f"""
            Section Text:
            {text}
        """
        response = self.client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=EXTRACTOR_SYSTEM_INSTRUCTION,
                temperature=0.0,
                response_mime_type="application/json",
                response_schema=ParsedSectionModel
            )
        )
        return cast(ParsedSectionModel, response.parsed)

    # ----------------------------
    # Main workflow
    # ----------------------------
    def run(
        self,
        file_path: str,
        document_text: str,
        model_overrides: Optional[Dict[str, str]] = None
    ) -> Iterator[DocumentParserEvent]:
        print("called")
        overrides = model_overrides or {}
        chunk_model = overrides.get("chunker", self.default_model)
        try:
            doc_chunks = self.chunk_document(document_text, chunk_model)
            if not doc_chunks:
                raise ValueError("doc analizer returned None")

            analyzed_data = self._to_analyzed_event_data(doc_chunks)
            yield {"event": "analyzed", "data": analyzed_data}
            results: List[ParsedDocumentSectionDTO] = []
            with ThreadPoolExecutor() as executor:
                future_to_title = {}
                for section in doc_chunks.sections:
                    title = section.title
                    m_name = overrides.get(title.lower(), self.default_model)
                    future = executor.submit(self.parse_section, section.text, m_name)
                    future_to_title[future] = title

                for future in as_completed(future_to_title):
                    title = future_to_title[future]
                    try:
                        # Get Pydantic model result
                        parsed_model = future.result()

                        # ADAPT: Convert Model to TypedDict
                        section_dict = self._to_section_event_data(title, parsed_model)
                        results.append(section_dict)
                        yield {
                            "event": "section_parsed",
                            "data": section_dict
                        }
                    except Exception as e:
                        yield {
                            "event": "error",
                            "data": f"Parsing section '{title}' failed: {str(e)}"
                        }
            # Yield Final Event (TypedDict)
            yield {
                "event": "final",
                "data": {
                    "request_id" : "",
                    "file_path" : file_path,
                    "file_hash" : "",
                    "metadata": json.dumps(analyzed_data["metadata"] , default=str),
                    "sections": cast(List[ParsedDocumentSectionDBModel] , results)
                }
            }
            validation_result = self.validate_document(
                full_text=document_text,
                metadata=analyzed_data["metadata"],
                sections=results,
                file_path=file_path,
                model_name="gemini-3-pro-preview"
            )
            # Decide which event to yield
            if getattr(validation_result, "status", "accepted"):
                yield {"event": "validation_accepted" , "data":None}
            else:
                # Convert ValidationResponseModel → ParsedDocumentDTO
                corrected_doc  = self._to_parsed_document_dto(validation_result,file_path)
                yield {"event": "validation_corrected", "data": corrected_doc}
        except Exception as e:
            yield {"event": "error", "data": f"Chunking failed: {str(e)}"}
            return


        # Yield Analyzed Event (TypedDict)
        # 2. Parallel Parsing Step

