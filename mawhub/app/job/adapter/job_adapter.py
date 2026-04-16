from typing import List, Protocol

from mawhub.app.job.adapter.job_workable_native_adapter import JobWorkableNativeAdapterInterface
from mawhub.mawhub.doctype.workable_candidate.workable_candidate import WorkableCandidateDBModel
from mawhub.mawhub.doctype.workable_event.workable_event import WorkableEventDBModel
from mawhub.mawhub.doctype.workable_job.workable_job import WorkableJobDBModel
from mawhub.mawhub.doctype.workable_job_candidate.workable_job_candidate import WorkableJobCandidateDBModel
from mawhub.mawhub.doctype.workable_job_stage.workable_job_stage import WorkableJobStageDBModel
from mawhub.mawhub.doctype.workable_stage.workable_stage import WorkableStageDBModel
from mawhub.pkg.workable.workable_types import WorkableCandidate, WorkableEvent, WorkableJob, WorkableStage


class JobWorkableAdapterInterface(Protocol):
    def stage_to_db(self, stage: WorkableStage) -> WorkableStageDBModel: ...
    def job_stage_row(self, stage: WorkableStage) -> WorkableJobStageDBModel: ...
    def candidate_to_db(
        self, candidate: WorkableCandidate, stage_lookup: dict[str, str]
    ) -> WorkableCandidateDBModel: ...
    def candidate_to_job_row(
        self, candidate: WorkableCandidate, stage_lookup: dict[str, str]
    ) -> WorkableJobCandidateDBModel: ...
    def event_to_db(self, event: WorkableEvent) -> WorkableEventDBModel: ...
    def job_to_db(
        self, job: WorkableJob, stages: List[WorkableStage]
    ) -> WorkableJobDBModel: ...


class JobAdapterInterface(Protocol):
    workable: JobWorkableAdapterInterface
    native: JobWorkableNativeAdapterInterface


class JobAdapter:
    workable: JobWorkableAdapterInterface
    native: JobWorkableNativeAdapterInterface

    def __init__(self) -> None:
        from mawhub.app.job.adapter.job_workable_adapter import JobWorkableAdapter
        from mawhub.app.job.adapter.job_workable_native_adapter import JobWorkableNativeAdapter
        self.workable = JobWorkableAdapter()
        self.native = JobWorkableNativeAdapter()
