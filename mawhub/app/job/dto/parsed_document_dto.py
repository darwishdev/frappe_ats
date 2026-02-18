# from typing import List, NotRequired, TypedDict
#
# # from mawhub.sqltypes.table_models import ParsedDocument, ParsedDocumentSection
#
# class ParsedSection(TypedDict, total=False):
#     name: str
#     description: NotRequired[str]
#     bullet_points: NotRequired[List[str]]
#     is_number_list: NotRequired[bool]
#     footer: NotRequired[str]
#
from mawhub.mawhub.doctype.parsed_document.parsed_document import ParsedDocumentDBModel
from mawhub.mawhub.doctype.parsed_document_section.parsed_document_section import ParsedDocumentSectionDBModel


class ParsedDocumentSectionDTO(ParsedDocumentSectionDBModel, total=False):
    pass
#     title: str
#     description: NotRequired[str]
#     bullet_points: NotRequired[str]
#     is_number_list: NotRequired[bool]
#     footer: NotRequired[str]
#
class ParsedDocumentDTO(ParsedDocumentDBModel , total=False):
    pass
#     file_path: str
#     file_hash: str
#     metadata: dict[str,str]
#     request_id: str
#     sections: List[ParsedDocumentSectionDTO]
# class ParsedDocumentOutput(TypedDict, total=False):
#     meta_data: dict[str,str]
#     sections: List[ParsedDocumentSectionDTO]
# class ParsedDocumentParseRequest(TypedDict, total=False):
#     path: str
#     parent_type: str
#     parent_id: str
# # This inherits all fields from ParsedDocument and adds 'sections'
# class ParsedDocumentWithSections(ParsedDocument):
#     sections: NotRequired[List[ParsedDocumentSection]]
