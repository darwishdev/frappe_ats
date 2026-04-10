from typing import cast

from mawhub.agent.question_bank_personalizer.types import (
    CandidateProfile,
    EvaluationCriteria,
    FollowupTrigger,
    JobObjectives,
    QuestionBankQuestion,
)
from mawhub.app.interview.repo.interview_types import (
    Candidate,
    InterviewFindResult,
    Job,
    Question,
    QuestionBank,
    Round,
)


class InterviewInterviewAdapter:

    def parse_interview_result(self, raw: dict) -> InterviewFindResult:
        return cast(InterviewFindResult, raw)

    def to_candidate_profile(self, candidate: Candidate) -> CandidateProfile:
        return CandidateProfile(
            applicant_name=candidate["name"] or "",
            job_title=candidate["designation"] or "",
            primary_skills=candidate["skills"] or [],
            summary=candidate["summary"] or "",
        )

    def to_job_objectives(self, job: Job, round_: Round) -> JobObjectives:
        must_have = [s["skill"] for s in (round_["expected_skills"] or []) if s.get("skill")]

        nice_to_have: list[str] = []
        for section in (job["description"] or []):
            if "requirement" in (section["title"] or "").lower():
                nice_to_have.extend(section["points"] or [])

        title_lower = (job["title"] or job["designation"] or "").lower()
        if any(w in title_lower for w in ("lead", "principal", "staff")):
            seniority = "Lead"
        elif any(w in title_lower for w in ("senior", "sr.")):
            seniority = "Senior"
        elif any(w in title_lower for w in ("junior", "jr.", "associate")):
            seniority = "Junior"
        else:
            seniority = "Mid"

        return JobObjectives(
            role_title=job["title"] or job["designation"] or "",
            must_have_skills=must_have,
            nice_to_have_skills=nice_to_have,
            seniority_level=seniority,
        )

    def to_question_bank_questions(self, question_bank: QuestionBank) -> list[QuestionBankQuestion]:
        return [self._to_question(q) for q in question_bank["questions"]]

    def _to_question(self, q: Question) -> QuestionBankQuestion:
        return QuestionBankQuestion(
            name=q["id"],
            category=q["category"],
            difficulty=q["difficulty"],  # type: ignore[arg-type]
            estimated_time_minutes=q["estimated_time_minutes"],
            question=q["question"],
            ideal_answer_keywords="\n".join(q["ideal_answer_keywords"]),
            evaluation_criteria=[
                EvaluationCriteria(
                    must_mention="\n".join(ec["must_mention"]),
                    bonus_points="\n".join(ec["bonus_points"]),
                )
                for ec in q["evaluation_criteria"]
            ],
            followup_triggers=[
                FollowupTrigger(condition=ft["condition"], follow_up=ft["follow_up"])
                for ft in q["followup_triggers"]
            ],
            pass_treshold=q["pass_threshold"],
        )
