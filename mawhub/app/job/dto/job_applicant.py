from typing import List, TypedDict


class JobApplicantUpdateRequest(TypedDict):
    name: str
    status: str
    pipeline_step: str

class JobApplicantBulkUpdateRequest(TypedDict):
    names: List[str]
    status: str
    pipeline_step: str

