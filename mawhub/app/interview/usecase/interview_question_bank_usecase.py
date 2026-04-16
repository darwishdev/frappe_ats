from typing import Protocol


from mawhub.agent.question_bank_personalizer.question_bank_personlaizer_agent import QuestionBankPersonalizerAgent
from mawhub.app.interview.adapter.interview_adapter import InterviewAdapterInterface
from mawhub.app.interview.repo.interview_interview_repo import InterviewDBModel
from mawhub.app.interview.repo.interview_repo import InterviewRepoInterface


class InterviewQuestionBankUsecaseInterface(Protocol):
    def personalize_question_bank(self, interview_id: str) -> str:...


class InterviewQuestionBankUsecase:
    repo: InterviewRepoInterface
    adapter: InterviewAdapterInterface
    question_bank_personalizer_agent: QuestionBankPersonalizerAgent
    def __init__(
        self,
        repo: InterviewRepoInterface,
        adapter: InterviewAdapterInterface,
        question_bank_personalizer_agent: QuestionBankPersonalizerAgent,
    ):
        self.repo = repo
        self.adapter = adapter
        self.question_bank_personalizer_agent = question_bank_personalizer_agent

    def personalize_question_bank(self, interview_id: str) -> str:
        # ── 1. Fetch & parse ───────────────────────────────────────────────
        raw = self.repo.interview.interview_find(interview_id)
        data = self.adapter.interview.parse_interview_result(raw)

        if not data.get("question_bank"):
            raise Exception(
                f"The job opening linked to interview {interview_id} has no question bank. "
                "Please generate a question bank on the Job Opening first."
            )
        if not data["question_bank"]["questions"]:
            raise Exception(f"Interview {interview_id} has no question bank or questions linked.")

        # ── 2. Convert repo types → agent inputs ───────────────────────────
        candidate = self.adapter.interview.to_candidate_profile(data["candidate"])
        job_objectives = self.adapter.interview.to_job_objectives(data["job"], data["round"])
        original_questions = self.adapter.interview.to_question_bank_questions(data["question_bank"])

        # ── 3. Run agent ───────────────────────────────────────────────────
        personalized_questions = self.question_bank_personalizer_agent.run(
            candidate=candidate,
            job_objectives=job_objectives,
            original_questions=original_questions,
        )

        # ── 4. Persist & return ────────────────────────────────────────────
        return self.repo.question_bank.save_personalized_question_bank(
            original_bank_name=data["question_bank"]["name"],
            interview_id=interview_id,
            personalized_questions=personalized_questions,
        )
