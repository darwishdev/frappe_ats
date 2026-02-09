import json
from time import sleep
from frappe import Union
from pydantic import BaseModel, Field
from typing import List, Literal, TypedDict
from google import genai
from google.genai import types
from typing import Dict, Iterator, Optional, Callable
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import cast


# ----------------------------
# Models
# ----------------------------
class DocumentSectionChunk(BaseModel):
    title: str = Field(
        description="Detected section header exactly as written in the document."
    )
    text: str = Field(
        description="Full original text belonging to this section. Do not summarize or rewrite."
    )

class DocumentMetaField(BaseModel):
    key: str = Field(
        description="Metadata field name found on the document. Examples: title, company, author, date, version, category, owner."
    )
    value: str = Field(
        description="Exact value of the metadata field as written in the document."
    )

class DocumentStructure(BaseModel):
    metadata: List[DocumentMetaField] = Field(
        description="List of key-value metadata pairs explicitly stated in the document header or introduction."
    )

    sections: List[DocumentSectionChunk] = Field(
        description="List of document sections identified by visible headers."
    )


class ParsedSection(BaseModel):
    description: Optional[str] = Field(
        default=None,
        description="Short explanation of what this section is about in 1–3 sentences."
    )

    is_number_list: bool = Field(
        default=False,
        description="True if the list uses numbers (e.g., 1., 2.), False if it uses symbols like ● or -."
    )

    bullet_points: Optional[List[str]] = Field(
        default_factory=list,
        description="Up to 5 key points extracted directly from the section text using original terminology."
    )

    footer: Optional[str] = Field(
        default=None,
        description="Paragraph text that appears after the bullet list. Preserve exact wording."
    )

class ParsedSectionEvent(TypedDict):
    title: Optional[str]
    description: Optional[str]
    is_number_list: bool
    footer: Optional[str]
    bullet_points: Optional[List[str]]
class ParsedDocumentFinalEvent(TypedDict):
    metadata: Dict[str,str]
    sections: List[ParsedSectionEvent]
class DocumentStructureEvent(TypedDict):
    metadata: Dict[str,str]
    parsed_sections: Dict[str,str]
class DocumentAnalyzedEvent(TypedDict):
    event: Literal["analyzed"]
    data: DocumentStructureEvent

# 2️⃣ Section parsed
class SectionParsedEvent(TypedDict):
    event: Literal["section_parsed"]
    data: ParsedSectionEvent

# 3️⃣ Workflow finished
class WorkflowFinalEvent(TypedDict):
    event: Literal["final"]
    data: ParsedDocumentFinalEvent

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

    def _to_analyzed_event_data(self, doc_chunks: DocumentStructure) -> DocumentStructureEvent:
        """Adapts Pydantic DocumentStructure to simplified TypedDict"""
        return {
            "metadata": {
                item.key: item.value for item in doc_chunks.metadata
            },
            "parsed_sections": {
                section.title: section.text for section in doc_chunks.sections
            }
        }
    def _to_section_event_data(self, title: str, section: ParsedSection) -> ParsedSectionEvent:
        """Adapts Pydantic ParsedSection to TypedDict ParsedSectionEvent"""
        return {
            "title": title,
            "description": section.description,
            "footer": section.footer,
            "is_number_list": section.is_number_list,
            "bullet_points": [
                bp.lstrip("●").strip() for bp in (section.bullet_points or [])
            ]
        }
    def get_text_hash(self, text: str) -> str:
        return hashlib.sha256(text.strip().encode("utf-8")).hexdigest()

    def chunk_document(self, text: str, model_name: str) -> DocumentStructure:
        SYSTEM_DOCUMENT_PARSER = """
            You are a structured document analyzer.

            Rules:
            - Work with any document type.
            - Never invent information.
            - Never guess missing metadata.
            - Preserve original wording when extracting.
            - Only extract what is explicitly present.
            - Follow the response JSON schema exactly.
            - Do not add extra fields.
            - Sections must be based only on real visible headers.
        """
        prompt = f"""
            Parsed Document Text:
            {text}
        """
        response = self.client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_DOCUMENT_PARSER,
                response_mime_type="application/json",
                response_schema=DocumentStructure
            )
        )
        return cast(DocumentStructure, response.parsed)

    def parse_section(self, text: str, model_name: str) -> ParsedSection:
        SYSTEM_SECTION_LAYOUT_EXTRACTOR = """
                You are a document section layout extractor.
                Your job is to split a section into structural parts based on visual markers.

                Detection Rules for Lists:
                - Identify a list by finding lines starting with symbols like '●', '•', '-', or numbers like '1.', '2.', 'a)'.
                - Specifically, look for the '●' symbol or '1.' numbering as primary indicators.

                Extraction Logic:
                - description: All text appearing BEFORE the first detected list item.
                - bullet_points: Each list item exactly as written but without the bullet symbol or
                  the number.
                - footer: All text appearing AFTER the final list item has ended.
                - is_number_list: Set to True if the list uses numbers (e.g., 1., 2.). Set to False if it uses symbols (e.g., ●, •).

                Strict Constraints:
                - DO NOT summarize or paraphrase.
                - Preserve original wording and formatting exactly.
                - If no list is found, bullet_points should be an empty list and is_number_list should be False.
                - Output must strictly follow the provided JSON schema.
            """
        prompt = f"""
            Analyze the following Section Text and split it into its structural components.

            Pay close attention to '1.' (numbered) or '●' (bulleted) indicators to determine where the list starts and ends.

            - Capture text before the indicators as 'description'.
            - Capture the lines starting with indicators as 'bullet_points'.
            - Capture any remaining text after the list as 'footer'.
            - Set 'is_number_list' based on the indicator type found.

            Section Text:
            {text}
        """
        response = self.client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_SECTION_LAYOUT_EXTRACTOR,
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
        print("text coming from the pdf")
        print(document_text)
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
            except Exception as e:
                yield {"event": "error", "data": f"Chunking failed: {str(e)}"}
                return

        # Yield Analyzed Event (TypedDict)
        analyzed_data = self._to_analyzed_event_data(doc_chunks)
        yield {"event": "analyzed", "data": analyzed_data}

        # 2. Parallel Parsing Step
        results: List[ParsedSectionEvent] = []
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
                "metadata": analyzed_data["metadata"],
                "sections": results
            }
        }
