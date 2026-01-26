from pydantic import BaseModel
from typing import List
from google import genai
from google.genai import types
from typing import Dict, Iterator, Optional, Callable
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import cast

# ----------------------------
# Models
# ----------------------------
class ChunkSection(BaseModel):
    title: str
    text: str

class MetaData(BaseModel):
    key: str
    value: str

class ChunkedDocument(BaseModel):
    metadata: List[MetaData]        # dynamic key-value pairs
    sections: List[ChunkSection]    # only headers

class ParsedDocumentSection(BaseModel):
    description: Optional[str] = None
    bullet_points: List[str] = []

# ----------------------------
# SSE Event type
# ----------------------------
from typing import TypedDict
class AgentEvent(TypedDict):
    event: str  # "update", "final", "error"
    data: dict

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

    # ----------------------------
    # Helpers
    # ----------------------------
    def get_text_hash(self, text: str) -> str:
        return hashlib.sha256(text.strip().encode("utf-8")).hexdigest()

    def chunk_document(self, text: str, model_name: str) -> ChunkedDocument:
        prompt = f"""
Extract dynamic metadata and structured sections from the job description.

1️⃣ Metadata:
- Extract all top-level key-value info at the start of the job description.
- Example: title, location, reports_to, company, department, etc.
- Return as a list of objects: key + value

2️⃣ Sections:
- Include only sections that start with a header (e.g., 'The Role', 'Key Responsibilities')
- For each section, return 'title' and 'text' fields
- Preserve original text

Return JSON exactly like this:

{{
  "metadata": [
    {{"key": "title", "value": "Finance Executive"}},
    {{"key": "location", "value": "Riyadh, Saudi Arabia"}}
  ],
  "sections": [
    {{"title": "The Role", "text": "We are hiring a Finance Executive ..."}},
    {{"title": "Key Responsibilities", "text": "Capital Strategy & Debt Management..."}}
  ]
}}

Job Description:
{text}
"""
        response = self.client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ChunkedDocument
            )
        )
        return cast(ChunkedDocument, response.parsed)

    def parse_section(self, title: str, text: str, model_name: str) -> ParsedDocumentSection:
        prompt = f"""
Parse this section into JSON matching ParsedDocumentSection:
- title
- description
- bullet_points (first 3 lines)
Preserve original terminology.

Text:
{text}
"""
        response = self.client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ParsedDocumentSection
            )
        )
        return cast(ParsedDocumentSection, response.parsed)

    # ----------------------------
    # Main workflow
    # ----------------------------
    def run(
        self,
        document_text: str,
        model_overrides: Optional[Dict[str, str]] = None
    ) -> Iterator[AgentEvent]:

        overrides = model_overrides or {}
        text_hash = self.get_text_hash(document_text)

        # ----------------------------
        # Step 1: Chunk + extract metadata
        # ----------------------------
        chunk_model = overrides.get("chunker", self.default_model)
        try:
            doc_chunks = self.chunk_document(document_text, chunk_model)
        except Exception as e:
            yield {"event": "error", "data": {"message": f"Chunking failed: {str(e)}"}}
            return

        # Yield metadata immediately
        metadata_dict = {meta.key: meta.value for meta in doc_chunks.metadata}
        chunk_titles = []
        for section in doc_chunks.sections:
            chunk_titles.append(section.title)
        yield {"event": "update", "data": {"metadata": metadata_dict , "titles" : chunk_titles}}

        # ----------------------------
        # Step 2: Parse sections in parallel
        # ----------------------------
        results: Dict[str, dict] = {}
        with ThreadPoolExecutor() as executor:
            future_to_title = {}
            for section in doc_chunks.sections:
                title = section.title
                text = section.text
                section_model = overrides.get(title.lower(), self.default_model)
                future = executor.submit(self.parse_section, title, text, section_model)
                future_to_title[future] = title

            for future in as_completed(future_to_title):
                title = future_to_title[future]
                try:
                    parsed_section = future.result()
                    section = parsed_section.model_dump()
                    results[title] = section
                    data = {}
                    data[title] = section
                    yield {"event": "update", "data": data}
                except Exception as e:
                    yield {"event": "error", "data": {"message": f"Parsing section '{title}' failed: {str(e)}"}}

        # ----------------------------
        # Step 3: Cache & final
        # ----------------------------
        if self.set_cache_fn:
            try:
                self.set_cache_fn(f"{text_hash}", self.default_model, results)
            except:
                pass

        yield {"event": "final", "data": results}
