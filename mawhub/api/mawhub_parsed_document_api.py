# from typing import Iterator, List, cast
# from frappe import _
# from mawhub.bootstrap import app_container
# from werkzeug.wrappers import Response
#
# from queue import Queue
# def adapter_to_parsed_document(
#     raw_data: Dict[str, Dict],
#     meta_data: Dict[str, str] = None,
#     file_name: str = "document.pdf",
#     parent_type: str = "job_description",
#     parent_id: str = ""
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
#             "pullet_points": content.get("bullet_points") or []
#         }
#         sections.append(section)
#
#     return {
#         "file": file_name,
#         "parent_type": parent_type,
#         "meta_data": meta_data or {},
#         "parent_id": parent_id,
#         "sections": sections
#     }
# How to use it in your run method:
# You can integrate this directly into your existing logic to transform the doc_chunks before yielding or returning.
#
# Python
# # Inside your run method logic:
# doc_data = { ... } # The dictionary from your prompt
# metadata = {meta.key: meta.value for meta in doc_chunks.metadata}
#
# parsed_dto = adapter_to_parsed_document(
#     raw_data=doc_data,
#     meta_data=metadata,
#     file_name="ejari_finance_exec.pdf"
# )
#
# yield {"event": "final_result", "data": parsed_dto}
