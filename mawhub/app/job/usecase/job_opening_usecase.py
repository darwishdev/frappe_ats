from frappe import _
from typing import Iterator, List, Protocol, cast
from mawhub.app.job.agent.document_parser_agent import DocumentParserWorkflow
from mawhub.app.job.agent.job_opening_parser import JobAgentEvent, JobOpeningAgentDTO, JobOpeningWorkflow
from mawhub.app.job.dto.job_opening import JobOpeningDTO, job_opening_list_sql_to_dto, job_opening_sql_to_dto
from mawhub.app.job.repo.job_repo import  JobRepoInterface
from mawhub.pkg.pdfconvertor.pdfconvertor import extract_text_from_pdf


class JobOpeningUsecaseInterface(Protocol):
    def job_opening_list(
        self,
        user_name: str,
    ) -> List[JobOpeningDTO]: ...

    def job_opening_parse(
        self,
        path: str,
    ) -> Iterator[JobAgentEvent]: ...
    def job_opening_find(
        self,
        job: str,
    ) -> JobOpeningDTO: ...
class JobOpeningUsecase:
    repo: JobRepoInterface
    job_agent: JobOpeningWorkflow
    document_parser_agent: DocumentParserWorkflow
    def __init__(
        self,
        repo: JobRepoInterface,
        job_agent: JobOpeningWorkflow,
        document_parser_agent: DocumentParserWorkflow,
    ):
        self.repo = repo
        self.job_agent = job_agent
        self.document_parser_agent = document_parser_agent

    def job_opening_list(
        self,
        user_name: str,
    ) -> List[JobOpeningDTO]:
        db_rows = self.repo.job_opening.job_opening_list(user_name)
        return job_opening_list_sql_to_dto(db_rows)

    def job_opening_find(
        self,
        job: str,
    ) -> JobOpeningDTO:
        db_rows = self.repo.job_opening.job_opening_find(job)
        return job_opening_sql_to_dto(db_rows)

    def _sse_events(
        self,
        resume_text: str,
    ) -> Iterator[JobAgentEvent]:
        if not resume_text.strip():
            raise ValueError("cant parse the resume text")
        final_resume: JobOpeningAgentDTO | None = None
        for update in self.job_agent.run(resume_text):
            yield update
            if isinstance(update, dict) and "data" in update:
                final_resume = cast(JobOpeningAgentDTO, update["data"])

        if not final_resume:
            raise ValueError("resume parsing finished without final result")

        yield {
            "event": "final",
            "data": final_resume,
        }
    def job_opening_parse(
        self,
        path:str,
    )->Iterator[JobAgentEvent]:
        txt = extract_text_from_pdf(path)
        try:
            for event in self._sse_events(
                txt,
            ):
                yield event
        except Exception as e:
            error_event: JobAgentEvent = {
                "event": "error",
                "data":  str(e),
            }
            yield error_event
