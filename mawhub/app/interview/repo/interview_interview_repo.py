from concurrent.futures import ThreadPoolExecutor
import frappe
from mawhub.pkg.baseclasses.app_repo import AppRepo
from typing import  Literal, NotRequired, Protocol, TypedDict, cast
from mawhub.pkg.baseclasses.app_repo import AppRepo, AppRepoInterface
from mawhub.pkg.overrides.job_opening import CustomJobOpening


class InterviewDBModel(TypedDict):
    name: NotRequired[str]

    # -------------------------
    # core interview fields
    # -------------------------
    interview_round: str
    job_applicant: str

    status: Literal[
        "Pending",
        "Under Review",
        "Cleared",
        "Rejected",
        "Cancelled",
    ]

    scheduled_on: str
    from_time: str
    to_time: str

    # -------------------------
    # ratings
    # -------------------------
    average_rating: float | None
    expected_average_rating: float | None

    # -------------------------
    # additional info
    # -------------------------
    interview_summary: NotRequired[str]
    resume_link: NotRequired[str]

    # -------------------------
    # derived / fetched fields
    # -------------------------
    job_opening: NotRequired[str]
    designation: NotRequired[str]

    # -------------------------
    # flags
    # -------------------------
    reminded: NotRequired[int]
    amended_from: NotRequired[str]
class InterviewInterviewRepoInterface(AppRepoInterface[InterviewDBModel],Protocol):
    def interview_find(self, name: str) -> dict:...




class InterviewInterviewRepo(AppRepo[InterviewDBModel]):
    def __init__(self):
        super().__init__(
            doc_name="Interview",
            name_key="name",
            scalar_fields=[
                "name",

                # core
                "interview_round",
                "job_applicant",
                "status",
                "scheduled_on",
                "from_time",
                "to_time",

                # ratings
                "average_rating",
                "expected_average_rating",

                # info
                "interview_summary",
                "resume_link",

                # derived
                "job_opening",
                "designation",

                # flags
                "reminded",
                "amended_from",
            ],
            child_tables={
                # optional if you later want interviewers
                # "interview_details": "Interview Detail"
            },
        )
    def interview_round_find(self,name : str):
        round = frappe.get_doc("Interview Round" , name)
        if not round:
            return {}
        response = {"interview_round" : round.as_dict()}
        interview_type_name = round.get("interview_type" , "")
        if not isinstance(interview_type_name,str):
            return {}
        interview_type_doc = frappe.get_doc("Interview Type" , interview_type_name)
        if interview_type_doc:
            response["interview_type"] = interview_type_doc.as_dict()
        return response

    def interview_find(self, name: str) -> dict:
        interview = frappe.get_doc("Interview", name)
        if not interview:
            return {}

        applicant_name = str(interview.get("job_applicant", ""))
        job_name = str(interview.get("custom_job_opening", ""))
        interview_round_name = str(interview.get("interview_round", ""))
        question_bank_name = str(interview.get("custom_question_bank", ""))
        site = frappe.local.site

        def run_in_frappe_context(fn, *args, **kwargs):
            try:
                frappe.init(site=site)
                frappe.connect()
                return fn(*args, **kwargs)
            finally:
                frappe.destroy()

        # --- Candidate ---
        def get_candidate_context(applicant_id: str) -> dict:
            applicant = frappe.get_doc("Job Applicant", applicant_id)
            if not applicant:
                return {}
            resume_name = applicant.get("resume_link", "")
            resume = frappe.get_doc("Applicant Resume", resume_name) if resume_name else None
            context = {
                "name": applicant.get("applicant_name", ""),
                "email": applicant.get("email_id", ""),
                "phone": applicant.get("phone_number", ""),
                "designation": applicant.get("designation", ""),
            }
            if resume:
                context["summary"] = resume.get("summary", "")
                context["skills"] = [
                    s.strip()
                    for s in (resume.get("skills") or "").split("\n")
                    if s.strip()
                ]
                context["experience"] = [
                    {
                        "company": e.get("company"),
                        "role": e.get("role"),
                        "from": e.get("from_date"),
                        "to": e.get("to_date"),
                        "responsibilities": [
                            r.strip()
                            for r in (e.get("responsibilities") or "").split("\n")
                            if r.strip()
                        ],
                    }
                    for e in (resume.get("experience") or [])
                ]
                context["education"] = [
                    {
                        "degree": e.get("degree"),
                        "institution": e.get("institution"),
                        "year": e.get("to_date"),
                    }
                    for e in (resume.get("education") or [])
                ]
                context["projects"] = [
                    {
                        "name": p.get("name") or p.get("title"),
                        "description": [
                            l.strip()
                            for l in (p.get("description") or "").split("\n")
                            if l.strip()
                        ],
                    }
                    for p in (resume.get("projects") or [])
                ]
            return {"candidate": context}

        # --- Job ---
        def get_job_context(job: str, applicant_id: str) -> dict:
            if not job:
                return {}
            job_opening = frappe.get_doc("Job Opening", job)
            if not job_opening:
                return {}
            job_opening = cast(CustomJobOpening, job_opening)

            context = {
                "id": job_opening.get("name"),
                "title": job_opening.get("job_title"),
                "designation": job_opening.get("designation"),
                "department": job_opening.get("department"),
                "location": job_opening.get("location"),
            }

            parsed_doc = job_opening.job_find_document()
            if parsed_doc:
                context["description"] = [
                    {
                        "title": s.get("title"),
                        "description": s.get("description"),
                        "points": [
                            p.strip()
                            for p in (s.get("bullet_points") or "").split("\n")
                            if p.strip()
                        ],
                    }
                    for s in (parsed_doc.get("sections") or [])
                ]

            _, resume_doc = job_opening.get_active_applicant_row_with_resume(applicant_id)
            pipeline_steps = job_opening.get("custom_pipeline_steps") or []
            current_step = next(
                (
                    {"code": s.get("step_code"), "name": s.get("step_name"), "type": s.get("step_type")}
                    for s in pipeline_steps
                    if s.get("step_type") == "interview"
                ),
                None,
            )
            if current_step:
                context["current_pipeline_step"] = current_step

            return {"job": context}

        # --- Interview Round ---
        def get_round_context(round_name: str) -> dict:
            if not round_name:
                return {}
            round_doc = frappe.get_doc("Interview Round", round_name)
            if not round_doc:
                return {}
            return {
                "round": {
                    "name": round_doc.get("round_name"),
                    "type": round_doc.get("interview_type"),
                    "designation": round_doc.get("designation"),
                    "expected_average_rating": round_doc.get("expected_average_rating"),
                    "expected_skills": [
                        {
                            "skill": s.get("skill"),
                            "description": s.get("description"),
                        }
                        for s in (round_doc.get("expected_skill_set") or [])
                    ],
                }
            }

        # --- Question Bank ---
        def get_question_bank_context(bank_name: str) -> dict:
            if not bank_name:
                return {}
            bank = frappe.get_doc("Question Bank", bank_name)
            if not bank:
                return {}
            question_names = [
                row.get("question_bank_question")
                for row in (bank.get("questions") or [])
                if row.get("question_bank_question")
            ]
            questions = []
            for qname in question_names:
                q = frappe.get_doc("Question Bank Question", qname)
                if not q:
                    continue
                questions.append({
                    "id": q.get("name"),
                    "category": q.get("category"),
                    "difficulty": q.get("difficulty"),
                    "estimated_time_minutes": q.get("estimated_time_minutes"),
                    "question": q.get("question"),
                    "ideal_answer_keywords": [
                        k.strip()
                        for k in (q.get("ideal_answer_keywords") or "").split("\n")
                        if k.strip()
                    ],
                    "evaluation_criteria": [
                        {
                            "must_mention": [
                                m.strip()
                                for m in (c.get("must_mention") or "").split("\n")
                                if m.strip()
                            ],
                            "bonus_points": [
                                b.strip()
                                for b in (c.get("bonus_points") or "").split("\n")
                                if b.strip()
                            ],
                        }
                        for c in (q.get("evaluation_criteria") or [])
                    ],
                    "followup_triggers": [
                        {
                            "condition": t.get("condition"),
                            "follow_up": t.get("follow_up"),
                        }
                        for t in (q.get("followup_triggers") or [])
                    ],
                    "pass_threshold": q.get("pass_treshold"),
                })
            return {
                "question_bank": {
                    "name": bank.get("name"),
                    "focus_areas": [
                        f.strip()
                        for f in (bank.get("focus_areas") or "").split("\n")
                        if f.strip()
                    ],
                    "questions": questions,
                }
            }

        # --- Run all in parallel ---
        with ThreadPoolExecutor(max_workers=4) as executor:
            future_candidate = executor.submit(run_in_frappe_context, get_candidate_context, applicant_name)
            future_job = executor.submit(run_in_frappe_context, get_job_context, job_name, applicant_name)
            future_round = executor.submit(run_in_frappe_context, get_round_context, interview_round_name)
            future_bank = executor.submit(run_in_frappe_context, get_question_bank_context, question_bank_name)

        return {
            "interview": {
                "id": interview.get("name"),
                "scheduled_on": str(interview.get("scheduled_on", "")),
                "designation": interview.get("designation"),
                "expected_average_rating": interview.get("expected_average_rating"),
                "status": interview.get("status"),
            },
            **future_candidate.result(),
            **future_job.result(),
            **future_round.result(),
            **future_bank.result(),
        }
