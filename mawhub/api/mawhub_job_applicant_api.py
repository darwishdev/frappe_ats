from typing import List
import frappe
from frappe import _
from mawhub.app.job.dto.job_applicant import JobApplicantBulkUpdateRequest, JobApplicantUpdateRequest
from mawhub.bootstrap import app_container
import pdfplumber
import os
import json
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor
import pdfplumber
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

# --- 1. Enhanced Schemas ---

class PersonalInfo(BaseModel):
    name: str
    email: str
    phone: str
    location: str
    links: List[str]

class ExperienceEntry(BaseModel):
    company: str
    role: str
    duration: str
    responsibilities: List[str]

class ExperienceList(BaseModel):
    items: List[ExperienceEntry]

class ProjectEntry(BaseModel):
    title: str
    tech_stack: List[str]
    description: str

class ProjectList(BaseModel):
    items: List[ProjectEntry]

class EducationEntry(BaseModel):
    institution: str
    degree: str
    location: str

class EducationList(BaseModel):
    items: List[EducationEntry]

class TextBlock(BaseModel):
    content: str

class ResumeSection(BaseModel):
    name: str = Field(description="One of: 'personal', 'summary', 'skills', 'experience', 'projects', 'education'")
    content: str

class ChunkedResume(BaseModel):
    sections: List[ResumeSection]

# --- 2. Workflow Logic ---

class ResumeWorkflow:
    def __init__(self):
        self.client = genai.Client(api_key="AIzaSyAersGfk7fX6R2sPt8VQy6ueDMGRaDpyTA")
        self.model_id = "gemini-2.0-flash"

    def agent_meta_labeler(self, raw_text: str) -> ChunkedResume:
        prompt = f"""
        Analyze this resume text and split it into these exact sections:
        'personal', 'summary', 'skills', 'experience', 'projects', 'education'.

        Text:
        {raw_text}
        """
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ChunkedResume
            )
        )
        return response.parsed

    def extraction_worker(self, section_name: str, text_chunk: str, schema: any):
        prompt = f"Extract structured data for the '{section_name}' section:\n\n{text_chunk}"
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=schema
            )
        )
        return response.parsed

    def run(self, resume_text: str):
        print("Agent 1: Labeling sections...")
        chunked_data = self.agent_meta_labeler(resume_text)

        # Mapping logic that covers your specific headers
        mapping = {
            "personal": PersonalInfo,
            "summary": TextBlock,
            "skills": TextBlock,
            "experience": ExperienceList,
            "projects": ProjectList,
            "education": EducationList
        }

        tasks = []
        for section in chunked_data.sections:
            clean_name = section.name.lower().strip()
            schema = mapping.get(clean_name)
            if schema:
                tasks.append((clean_name, section.content, schema))

        print(f"Spinning up parallel workers for {len(tasks)} sections: {[t[0] for t in tasks]}")

        results = {}
        with ThreadPoolExecutor() as executor:
            future_to_section = {
                executor.submit(self.extraction_worker, name, text, schema): name
                for name, text, schema in tasks
            }
            for future in future_to_section:
                name = future_to_section[future]
                results[name] = future.result()

        return results

def extract_text_from_pdf(pdf_path: str) -> str:
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

@frappe.whitelist(methods=["PUT","POST"], allow_guest=True)
def job_applicant_create(payload:str)->str:
    txt = extract_text_from_pdf(payload)
    workflow = ResumeWorkflow()
    final_json = workflow.run(txt)
    print("\n--- Final Structured Data ---")
    output = {k: v.model_dump() for k, v in final_json.items()}
    return json.dumps(output)

@frappe.whitelist(methods=["PUT","POST"], allow_guest=True)
def job_applicant_bulk_update(payload:JobApplicantBulkUpdateRequest)->List[str]:
    return app_container.job_usecase.job_applicant.job_applicant_bulk_update(payload)

@frappe.whitelist(methods=["PUT","POST"], allow_guest=True)
def job_applicant_update(payload:JobApplicantUpdateRequest)->str:
    return app_container.job_usecase.job_applicant.job_applicant_update(payload)
