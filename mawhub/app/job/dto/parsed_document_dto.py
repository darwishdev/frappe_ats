from typing import List, NotRequired, TypedDict

class ParsedDocumentSectionDTO(TypedDict, total=False):
    title: str
    description: NotRequired[str]
    pullet_points: NotRequired[List[str]]
    sections: NotRequired[List[ParsedDocumentSectionDTO]]

class ParsedDocumentDTO(TypedDict, total=False):
    file: str
    parent_type: str
    meta_data: dict[str,str]
    parent_id: str
    sections: List[ParsedDocumentSectionDTO]
