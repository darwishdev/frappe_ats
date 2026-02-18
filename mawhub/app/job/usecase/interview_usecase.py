# from frappe import _
# from typing import  Protocol, TypedDict
# from mawhub.app.job.repo.job_repo import JobRepoInterface
# # from mawhub.sqltypes.table_models import Interview
# class Interview(TypedDict):
#     ...
#
# class InterviewUsecaseInterface(Protocol):
#     def interview_create_update(self, payload: Interview)->Interview:...
# class InterviewUsecase:
#     repo: JobRepoInterface
#     def __init__(
#         self,
#         repo: JobRepoInterface,
#     ):
#         self.repo = repo
#
#     def interview_create_update(self, payload: Interview)->Interview:
#         return self.repo.interview.interview_create_update(payload)
#
