import json
from typing import Dict,  List
from mawhub.bootstrap import app_container
from frappe import _
import frappe
from mawhub.app.job.dto.parsed_document_dto import ParsedDocumentDTO, ParsedDocumentSectionDTO

# def parsed_document_from_agent_to_dto(
#     raw_data: Dict[str, Dict],
#     meta_data: Dict[str, str],
#     file_name: str,
#     parent_type: str,
#     parent_id: str
# ) -> ParsedDocumentDTO:
#     """
#     Adapts raw chunked data into a structured ParsedDocumentDTO.
#     """
#     sections: List[ParsedDocumentSectionDTO] = []
#
#     for title, content in raw_data.items():
#         # Create the section object
#         section: ParsedDocumentSectionDTO = {
#             "title": title,
#             "description": content.get("description") or "",
#             "pullet_points": json.dumps(content.get("bullet_points"),default=str) or ""
#         }
#         sections.append(section)
#
#     return {
#         "file": file_name,
#         "file_hash" : "asd",
#         "parent_type": parent_type,
#         "meta_data": json.dumps(meta_data) or "",
#         "parent_id": parent_id,
#         "sections": sections
#     }




@frappe.whitelist(methods=["PUT" , "POST"], allow_guest=True)
def parsed_document_create_update(payload:ParsedDocumentDTO):
    return app_container.job_usecase.parsed_document.parsed_document_create_update(payload)

