from google.genai.client import Client
from mawhub.agent.document_parser.document_parser_agent import DocumentParserWorkflow
from mawhub.agent.file_text_parser.file_text_parser_agent import FileTextParserWorkflow
from mawhub.agent.job_opening_parser.job_opening_parser_agent import JobOpeningParserWorkflow
from mawhub.agent.resume_parser.resume_parser_agent import ResumeWorkflow
from mawhub.app.applicant.repo.applicant_repo import ApplicantRepo
from mawhub.app.applicant.usecase.applicant_usecase import ApplicantUsecase, ApplicantUsecaseInterface
from mawhub.app.job.repo.job_repo import JobRepo
from mawhub.app.job.usecase.job_usecase import JobUseCase, JobUseCaseInterface


class AppContainer:
    """
    Application-level dependency container.
    Owns object graph and lifecycle.
    """
    job_usecase: JobUseCaseInterface
    applicant_usecase: ApplicantUsecaseInterface

    def __init__(self,gemini_api_key:str):
        model_name = 'gemini-2.5-flash-lite'
        job_repo = JobRepo()
        applicant_repo = ApplicantRepo()
        gemini_api_client = Client(api_key=gemini_api_key)
        resume_parser_agent = ResumeWorkflow(client=gemini_api_client,model_name=model_name)
        job_opening_parser_agent = JobOpeningParserWorkflow(client=gemini_api_client,model_name=model_name)
        document_parser_agent = DocumentParserWorkflow(client=gemini_api_client,model_name=model_name)
        file_text_parser_agent = FileTextParserWorkflow(client=gemini_api_client,model_name=model_name)
        job_usecase = JobUseCase(
            job_repo=job_repo,
            file_text_parser_agent=file_text_parser_agent,
            resume_parser_agent=resume_parser_agent,
            job_opening_parser_agent=job_opening_parser_agent,
            document_parser_agent=document_parser_agent,
        )
        applicant_usecase = ApplicantUsecase(
            repo=applicant_repo,
            file_text_parser_agent=file_text_parser_agent,
            resume_parser_agent=resume_parser_agent,
        )
        self.job_usecase = job_usecase
        self.applicant_usecase = applicant_usecase

