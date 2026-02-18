# Copyright (c) 2026, darwishdev and contributors
# For license information, please see license.txt

# import frappe
from typing import NotRequired, TypedDict
from frappe.model.document import Document

class ParsedDocumentSectionDBModel(TypedDict):
    # frappe child meta
    name: NotRequired[str]
    parent: NotRequired[str]
    parentfield: NotRequired[str]
    parenttype: NotRequired[str]
    idx: NotRequired[int]

    # fields
    title: str
    description: NotRequired[str]
    bullet_points: NotRequired[str]
    footer: NotRequired[str]
    is_number_list: NotRequired[bool]

class ParsedDocumentSection(Document):
	pass
