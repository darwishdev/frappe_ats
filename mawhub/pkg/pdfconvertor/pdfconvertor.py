import hashlib
import os
import frappe
import pdfplumber
from typing import Tuple
from pathlib import Path

def extract_text_from_pdf(pdf_path: str) -> str:
    # If the path starts with '/', prepend SITE_ROOT
    if pdf_path.startswith("/"):
        site_name = frappe.local.site  # current site name
        pdf_path = os.path.join(site_name, pdf_path.lstrip("/"))

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:  # avoid appending None
                text += page_text + "\n"


    return text

def get_text_hash(text: str) -> str:
    clean_text = text.strip().encode('utf-8')
    return hashlib.sha256(clean_text).hexdigest()

def get_document_content_and_hash(file_path: str) -> Tuple[str, str]:
    txt = extract_text_from_pdf(file_path)
    file_hash = get_text_hash(txt)
    return txt, file_hash
