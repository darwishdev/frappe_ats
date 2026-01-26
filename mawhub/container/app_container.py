from google.genai.client import Client
from mawhub.app.job.repo.job_repo import JobRepo
from mawhub.app.job.usecase.job_usecase import JobUseCase, JobUseCaseInterface


class AppContainer:
    """
    Application-level dependency container.
    Owns object graph and lifecycle.
    """
    job_usecase: JobUseCaseInterface

    def __init__(self,gemini_api_key:str):
        job_repo = JobRepo()
        gemini_api_client = Client(api_key=gemini_api_key)
        job_usecase = JobUseCase(job_repo=job_repo,gemini_api_client=gemini_api_client)
        self.job_usecase = job_usecase

