# Copyright (c) 2026, darwishdev and contributors
# For license information, please see license.txt

# import frappe
from typing import List, NotRequired, TypedDict
from frappe.model.document import Document

from mawhub.mawhub.doctype.parsed_document_section.parsed_document_section import ParsedDocumentSectionDBModel


class ParsedDocumentDBModel(TypedDict):
    # -------------------------
    # frappe system fields
    # -------------------------
    name: NotRequired[str]
    idx: NotRequired[int]

    # -------------------------
    # scalar fields
    # -------------------------
    file_path: str
    file_hash: str
    metadata: NotRequired[str]
    request_id: str

    # -------------------------
    # child tables
    # -------------------------
    sections: List[ParsedDocumentSectionDBModel]

class ParsedDocument(Document):
    pass
