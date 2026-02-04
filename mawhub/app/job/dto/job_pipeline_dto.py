from typing import  List, NotRequired,  TypedDict
class JobPipelineStep(TypedDict):
    step_code: str
    step_name: str
    step_type: str

class JobPipelineCreateRequest(TypedDict):
    name: str
    description: NotRequired[str]
    steps: List[JobPipelineStep]
