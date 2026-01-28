import json
from typing import List, NotRequired, TypedDict

from mawhub.sqltypes.table_models import ParsedDocument, ParsedDocumentSection

class ParsedDocumentSectionDTO(TypedDict, total=False):
    title: str
    description: NotRequired[str]
    pullet_points: NotRequired[List[str]]

class ParsedDocumentDTO(TypedDict, total=False):
    file: str
    file_hash: str
    parent_type: str
    meta_data: dict[str,str]
    parent_id: str
    sections: List[ParsedDocumentSectionDTO]
# This inherits all fields from ParsedDocument and adds 'sections'
class ParsedDocumentWithSections(ParsedDocument):
    sections: NotRequired[List[ParsedDocumentSection]]
def parsed_document_dto_to_sql(dto: ParsedDocumentDTO) -> ParsedDocumentWithSections:
    """
    Converts ParsedDocumentDTO (client-side format)
    to ParsedDocumentWithSections (Frappe-compatible format).
    """
    # Create a copy to avoid mutating the original input unexpectedly
    adapted_data: ParsedDocumentWithSections = dict(dto) # type: ignore
    meta_data = adapted_data.get('meta_data')
    if isinstance(meta_data , dict):
        adapted_data['meta_data'] = json.dumps(meta_data)
        # setattr(adapted_data , "meta_data" , meta_data)
    sections = adapted_data.get("sections", [])

    for section in sections:
        points = section.get("pullet_points")
        section["pullet_points"] = json.dumps(points)

    return adapted_data
