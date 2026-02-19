import hashlib
import json
from docx import Document
import os
import frappe
import pdfplumber
from typing import Tuple, TypedDict
from pathlib import Path

class FileData(TypedDict):
    file_type: str        # mime type e.g. "application/pdf"
    file_path: str        # full resolved path
    file_name: str        # just the file name
    file_bytes: bytes     # file contents

def read_file_data(file_path: str) -> FileData:
    """
    Reads any file from Frappe private/public folder or absolute path.
    Returns a FileData dict containing type, name, path, and bytes.
    """
    # Resolve Frappe site path
    if file_path.startswith("/"):
        site_root = frappe.local.site
        file_path = os.path.join(site_root, file_path.lstrip("/"))

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    file_name = os.path.basename(file_path)
    file_ext = os.path.splitext(file_name)[1].lower()

    # Determine mime type (very basic)
    mime_map = {
        ".pdf": "application/pdf",
        ".txt": "text/plain",
        ".csv": "text/csv",
        ".json": "application/json"
    }
    file_type = mime_map.get(file_ext, "application/octet-stream")

    with open(file_path, "rb") as f:
        file_bytes = f.read()

    return FileData(
        file_type=file_type,
        file_path=file_path,
        file_name=file_name,
        file_bytes=file_bytes
    )
def read_pdf_bytes(pdf_path: str) -> bytes:
    """
    Reads PDF file bytes from a Frappe private/public file path.
    """
    # Prepend site root if path starts with '/'
    if pdf_path.startswith("/"):
        site_root = frappe.local.site  # current site name
        pdf_path = os.path.join(site_root, pdf_path.lstrip("/"))

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    with open(pdf_path, "rb") as f:
        return f.read()
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

def extract_text_from_txt(txt_path: str) -> str:
    with open(txt_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def extract_text_from_docx(docx_path: str) -> str:
    doc = Document(docx_path)
    return "\n".join(p.text for p in doc.paragraphs)
def get_document_content_and_hash(file_path: str) -> Tuple[str, str]:
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        text = extract_text_from_pdf(file_path)
    elif ext == ".txt":
        text = extract_text_from_txt(file_path)
    elif ext == ".json":
        text = extract_text_from_json(file_path)
    elif ext == ".docx":
        text = extract_text_from_docx(file_path)
    # elif ext == ".doc":
    #     text = extract_text_from_doc(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")
    file_hash = get_text_hash(text)
    return text, file_hash

