# mawhub/app/job/dto/communication.py
from pydantic import BaseModel, Field
import json
from typing import Optional, Dict, cast
from google.genai import types, Client
from pydantic import BaseModel
class AIEmailResponse(BaseModel):
    subject: str = Field(description="A professional email subject line")
    message: str = Field(description="The full body of the email in HTML format")

class CommunicationWorkflow:
    def __init__(self, client: Client, model_name: str):
        self.client = client
        self.default_model = model_name

    def generate_candidate_email(
        self,
        job_info: dict,           # Data from AIJobOpeningExtraction
        applicant_info: dict,     # Data from ApplicantResumeDTO
        pipeline_step: str,       # e.g., "Technical Interview", "Rejection", "Offer"
        user_instructions: Optional[str] = None
    ) -> AIEmailResponse:

        # Prepare context for the AI
        prompt = f"""
        Act as an expert HR Recruiter at Ejari. Write a professional, warm, and clear email to a candidate.

        CONTEXT:
        - Candidate Name: {applicant_info.get('personal', {}).get('full_name', 'Candidate')}
        - Job Title: {job_info.get('job_title')}
        - Current Pipeline Stage: {pipeline_step}

        JOB DESCRIPTION SUMMARY:
        {job_info.get('description')[:500]}...

        CANDIDATE SUMMARY:
        {applicant_info.get('summary', 'A qualified professional.')}

        SPECIAL INSTRUCTIONS FROM RECRUITER:
        {user_instructions or "Draft a standard professional update for this stage."}

        OUTPUT REQUIREMENTS:
        - Use a friendly but professional tone.
        - Use HTML for line breaks (<br>) if needed.
        - Return ONLY JSON matching the schema.
        """

        response = self.client.models.generate_content(
            model=self.default_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=AIEmailResponse,
                temperature=0.7 # Higher temperature for more natural writing
            )
        )

        # Silent parsing
        return cast(AIEmailResponse, response.parsed)
