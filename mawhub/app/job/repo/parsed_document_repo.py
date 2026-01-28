from typing import  Protocol
from mawhub.app.job.dto.parsed_document_dto import ParsedDocumentDTO, ParsedDocumentWithSections
from mawhub.pkg.baseclasses.app_repo import AppRepo, AppRepoInterface
from mawhub.sqltypes.table_models import ParsedDocument


class ParsedDocumentRepoInterface(AppRepoInterface[ParsedDocumentWithSections],Protocol):
    pass



class ParsedDocumentRepo(AppRepo[ParsedDocumentWithSections]):
    def __init__(self):
        super().__init__(
            doc_name="Parsed Document",
            name_key="file",
            scalar_fields=[
                "file",
                "file_hash",
                "meta_data",
                "parent_id",
                "parent_type",
            ],
            child_tables={
                "sections": "sections",
            },
        )
