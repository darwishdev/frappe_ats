from typing import  Protocol
from mawhub.mawhub.doctype.parsed_document.parsed_document import ParsedDocumentDBModel
from mawhub.pkg.baseclasses.app_repo import AppRepo, AppRepoInterface


class ParsedDocumentRepoInterface(AppRepoInterface[ParsedDocumentDBModel],Protocol):
    pass

class ParsedDocumentRepo(AppRepo[ParsedDocumentDBModel]):
    def __init__(self):
        super().__init__(
            doc_name="Parsed Document",
            name_key="file",
            scalar_fields=[
                "name",
                "file_path",
                "output",
                "file_hash",
                "metadata",
                "request_id",
            ],
            child_tables=["sections"]
        )
