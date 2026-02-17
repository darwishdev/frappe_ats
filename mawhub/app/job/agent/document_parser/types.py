from pydantic import BaseModel, Field
from typing import List
from typing import  Optional
# ----------------------------
# Models
# ----------------------------
class DocumentSectionChunkModel(BaseModel):
    title: str = Field(
        description="Detected section header exactly as written in the document."
    )
    text: str = Field(
        description="Full original text belonging to this section. Do not summarize or rewrite."
    )

class DocumentMetaFieldModel(BaseModel):
    key: str = Field(
        description="Metadata field name found on the document. Examples: title, company, author, date, version, category, owner."
    )
    value: str = Field(
        description="Exact value of the metadata field as written in the document."
    )

class DocumentStructureModel(BaseModel):
    metadata: List[DocumentMetaFieldModel] = Field(
        description="List of key-value metadata pairs explicitly stated in the document header or introduction."
    )

    sections: List[DocumentSectionChunkModel] = Field(
        description="List of document sections identified by visible headers."
    )


class ParsedSectionModel(BaseModel):
    description: Optional[str] = Field(
        default=None,
        description="Short explanation of what this section is about in 1–3 sentences."
    )

    is_number_list: bool = Field(
        default=False,
        description="True if the list uses numbers (e.g., 1., 2.), False if it uses symbols like ● or -."
    )

    bullet_points: Optional[List[str]] = Field(
        default_factory=list,
        description="Up to 5 key points extracted directly from the section text using original terminology."
    )

    footer: Optional[str] = Field(
        default=None,
        description="Paragraph text that appears after the bullet list. Preserve exact wording."
    )
