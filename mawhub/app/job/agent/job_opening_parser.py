# mawhub/app/job/agent/job_opening_workflow.py
import hashlib
import json
from typing import Dict, Optional, cast
from google.genai import types, Client
from pydantic import BaseModel

from mawhub.app.job.agent.document_parser_agent import ChunkedDocument

class AIJobOpeningExtraction(BaseModel):
    """The AI only extracts these specific fields from the text"""
    job_title: str
    description: str
    location: Optional[str] = None
    lower_range: Optional[float] = 0.0
    upper_range: Optional[float] = 0.0
    currency: Optional[str] = "SAR"

class JobOpeningWorkflow:
    def __init__(
        self,
        client: Client,
        model_name: str,
        get_cache_fn=None,
        set_cache_fn=None
    ):
        self.client = client
        self.default_model = model_name
        self.get_cache_fn = get_cache_fn
        self.set_cache_fn = set_cache_fn

    def get_text_hash(self, text: str) -> str:
        # Consistency with your resume agent's hashing style
        return hashlib.md5(text.encode('utf-8')).hexdigest()

    def run(
        self,
        chunked_doc: dict,
        model_overrides: Optional[Dict[str, str]] = None
    ) -> AIJobOpeningExtraction:
        overrides = model_overrides or {}
        model_id = overrides.get("model", self.default_model)

        # 1. Create a stable hash for caching
        full_content = json.dumps(chunked_doc, sort_keys=True)
        text_hash = self.get_text_hash(full_content)

        # 2. Check Cache
        # if self.get_cache_fn:
        #     cached_data = self.get_cache_fn(text_hash, model_id)
        #     if cached_data:
        #         # If cached as string, parse it; if dict, unpack it
        #         data = json.loads(cached_data) if isinstance(cached_data, str) else cached_data
        #         return AIJobOpeningExtraction(**data)

        # 3. Prepare Extraction Prompt
        # Passing raw JSON to the prompt is fine, but we give Gemini context
        prompt = f"""
        Extract job details from the following structured document sections.
        Focus on the job title, description, location, and salary ranges.

        DOCUMENT SECTIONS:
        {full_content}
        """

        # 4. Call Gemini with Native Parsing (response.parsed)
        response = self.client.models.generate_content(
            model=model_id,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=AIJobOpeningExtraction,
                temperature=0.1
            )
        )

        # 5. Robust Extraction (Silent Fix)
        # Using .parsed is the SDK's built-in way to get the Pydantic object directly
        validated_data = cast(AIJobOpeningExtraction, response.parsed)

        # Fallback if .parsed failed but .text exists
        if not validated_data and response.text:
            try:
                # Clean markdown if AI ignored the mime_type instruction
                clean_text = response.text.strip().strip('`').replace('json', '', 1).strip()
                validated_data = AIJobOpeningExtraction(**json.loads(clean_text))
            except Exception:
                # Last resort: empty model or handle as error
                raise ValueError("Failed to parse AI response into AIJobOpeningExtraction mapping")

        # 6. Save to Cache
        if self.set_cache_fn and validated_data:
            try:
                self.set_cache_fn(text_hash, model_id, validated_data.model_dump())
            except:
                pass

        return validated_data
