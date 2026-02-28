from mawhub.app.applicant.dto.applicant_resume_dto import ApplicantResumeDTO
from mawhub.app.applicant.repo.job_applicant_repo import JobApplicantDBModel

def job_applicant_dto_from_resume(agent_final: ApplicantResumeDTO,path:str) -> JobApplicantDBModel:
    """Minimal conversion with only essential fields mapped."""
    resp : JobApplicantDBModel = {
        "lower_range": 0.0,
        "designation": agent_final.get("job_title") or "",
        "upper_range": 0.0,
        "status": "Open",
        "resume_attachment":path,
        "applicant_rating": 0.0,
        "applicant_name": agent_final.get("name", ""),
        "email_id": agent_final.get("email", ""),
        "phone_number": agent_final.get("phone", ""),
        # "country": personal.get("location", ""),
    }
    return resp
#
#
