from typing import  Protocol
from mawhub.app.job.dto.parsed_document_dto import ParsedDocumentDTO
from mawhub.pkg.baseclasses.app_repo import AppRepo, AppRepoInterface


class ParsedDocumentRepoInterface(AppRepoInterface[ParsedDocumentDTO],Protocol):
    pass



class ParsedDocumentRepo(AppRepo[ParsedDocumentDTO]):
    def __init__(self):
        super().__init__(
            doc_name="Parsed Document",
            name_key="file",
            scalar_fields=[
                "file",
                "meta_data",
                "parent_id",
                "parent_type",
            ],
            child_tables={
                "sections": "sections",
            },
        )
