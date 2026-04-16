from typing import Protocol

from mawhub.app.job.repo.job_opening_repo import JobOpeningRepo, JobOpeningRepoInterface
from mawhub.app.job.repo.job_pipeline_repo import JobPipelineRepo, JobPipelineRepoInterface
from mawhub.app.job.repo.parsed_document_repo import ParsedDocumentRepo, ParsedDocumentRepoInterface
from mawhub.app.job.repo.workable_stage_repo import WorkableStageRepo, WorkableStageRepoInterface
from mawhub.app.job.repo.workable_candidate_repo import WorkableCandidateRepo, WorkableCandidateRepoInterface
from mawhub.app.job.repo.workable_job_repo import WorkableJobRepo, WorkableJobRepoInterface
from mawhub.app.job.repo.workable_event_repo import WorkableEventRepo, WorkableEventRepoInterface


class JobRepoInterface(Protocol):
    job_opening: JobOpeningRepoInterface
    job_pipeline: JobPipelineRepoInterface
    parsed_document: ParsedDocumentRepoInterface
    workable_stage: WorkableStageRepoInterface
    workable_candidate: WorkableCandidateRepoInterface
    workable_job: WorkableJobRepoInterface
    workable_event: WorkableEventRepoInterface


class JobRepo:
    job_opening: JobOpeningRepoInterface
    job_pipeline: JobPipelineRepoInterface
    parsed_document: ParsedDocumentRepoInterface
    workable_stage: WorkableStageRepoInterface
    workable_candidate: WorkableCandidateRepoInterface
    workable_job: WorkableJobRepoInterface
    workable_event: WorkableEventRepoInterface

    def __init__(self):
        self.job_opening = JobOpeningRepo()
        self.job_pipeline = JobPipelineRepo()
        self.parsed_document = ParsedDocumentRepo()
        self.workable_stage = WorkableStageRepo()
        self.workable_candidate = WorkableCandidateRepo()
        self.workable_job = WorkableJobRepo()
        self.workable_event = WorkableEventRepo()
