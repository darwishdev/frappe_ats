
import json
from mawhub.app.job.agent.document_parser.instructions import CUNKER_SYSTEM_INSTRUCTION, EXTRACTOR_SYSTEM_INSTRUCTION
from frappe import Union
from typing import List, Literal, TypedDict
from google import genai
from google.genai import types
from typing import Dict, Iterator, Optional, Callable
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import cast

from mawhub.app.job.agent.document_parser.types import DocumentStructureModel, ParsedSectionModel
from mawhub.app.job.dto.parsed_document_dto import ParsedDocumentDTO, ParsedDocumentSectionDTO, ParsedSection

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

DocumentParserEvent = Union[
    DocumentAnalyzedEvent,
    SectionParsedEvent,
    WorkflowFinalEvent,
    WorkflowErrorEvent
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
        data: ParsedDocumentSectionDTO = {
            "title": section_name,
        }

        if section.description is not None:
            data["description"] = section.description

        if section.footer is not None:
            data["footer"] = section.footer

        if section.is_number_list is not None:
            data["is_number_list"] = section.is_number_list

        if section.bullet_points is not None:
            data["bullet_points"] = section.bullet_points
        return data
    def get_text_hash(self, text: str) -> str:
        return hashlib.sha256(text.strip().encode("utf-8")).hexdigest()

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

    def parse_section(self, text: str, model_name: str) -> ParsedSection:
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
                response_schema=ParsedSection
            )
        )
        return cast(ParsedSection, response.parsed)

    # ----------------------------
    # Main workflow
    # ----------------------------
    def run(
        self,
        document_text: str,
        model_overrides: Optional[Dict[str, str]] = None
    ) -> Iterator[DocumentParserEvent]:
        overrides = model_overrides or {}
        cache_key = self.get_text_hash(document_text)
        if self.get_cache_fn:
            cached_str = self.get_cache_fn(cache_key, self.default_model)
            if isinstance(cached_str,str):
                cached = json.loads(cached_str)
                if cached:
                    yield {"event": "final", "data": cached}
                    return

            # 1. Analysis Step
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
                            # Yield Section Parsed Event (TypedDict)
                            yield {
                                "event": "section_parsed",
                                "data": section_dict
                            }
                        except Exception as e:
                            yield {
                                "event": "error",
                                "data": f"Parsing section '{title}' failed: {str(e)}"
                            }
                final_data = {
                        "metadata": analyzed_data["metadata"],
                        "sections": results
                    }
                if self.set_cache_fn:
                    self.set_cache_fn(cache_key, self.default_model, final_data)

                # 3. Final Step
                # Yield Final Event (TypedDict)
                yield {
                    "event": "final",
                    "data": {
                        "request_id" : "",
                        "file_path" : "",
                        "file_hash" : "",
                        "metadata": analyzed_data["metadata"],
                        "sections": results
                    }
                }
            except Exception as e:
                yield {"event": "error", "data": f"Chunking failed: {str(e)}"}
                return


        # Yield Analyzed Event (TypedDict)
        # 2. Parallel Parsing Step

