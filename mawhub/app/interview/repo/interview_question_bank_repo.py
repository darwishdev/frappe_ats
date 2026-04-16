from typing import NotRequired, Protocol, TypedDict
import frappe

from mawhub.agent.question_bank_personalizer.types import PersonalizedQuestionBankQuestion
from mawhub.pkg.baseclasses.app_repo import AppRepo, AppRepoInterface


class QuestionBankDBModel(TypedDict):
    name: NotRequired[str]
    focus_areas: NotRequired[str]


class InterviewQuestionBankRepoInterface(AppRepoInterface[QuestionBankDBModel], Protocol):
    def save_personalized_question_bank(
        self,
        original_bank_name: str,
        interview_id: str,
        personalized_questions: list[PersonalizedQuestionBankQuestion],
    ) -> str: ...


class InterviewQuestionBankRepo(AppRepo[QuestionBankDBModel]):
    def __init__(self):
        super().__init__(
            doc_name="Question Bank",
            name_key="name",
            scalar_fields=[
                "name",
                "focus_areas",
            ],
            child_tables={
                "questions": "Question Bank Question Link",
            },
        )

    def save_personalized_question_bank(
        self,
        original_bank_name: str,
        interview_id: str,
        personalized_questions: list[PersonalizedQuestionBankQuestion],
    ) -> str:
        question_names: list[str] = []

        for pq in personalized_questions:
            q_doc = frappe.new_doc("Question Bank Question")
            q_doc.name = f"{pq.name}-{interview_id}"
            q_doc.set("category" , pq.category)
            q_doc.set("difficulty" , pq.difficulty)
            q_doc.set("estimated_time_minutes" , pq.estimated_time_minutes)
            q_doc.set("question" , pq.question)
            q_doc.set("ideal_answer_keywords" , pq.ideal_answer_keywords)
            q_doc.set("pass_treshold" , pq.pass_treshold)

            for ec in pq.evaluation_criteria:
                q_doc.append("evaluation_criteria", {
                    "must_mention": ec.must_mention,
                    "bonus_points": ec.bonus_points,
                })

            for ft in pq.followup_triggers:
                q_doc.append("followup_triggers", {
                    "condition": ft.condition,
                    "follow_up": ft.follow_up,
                })

            q_doc.insert(ignore_permissions=True)
            question_names.append(q_doc.name)

        bank_doc = frappe.new_doc("Question Bank")
        bank_doc.name = f"{original_bank_name}-{interview_id}"

        for qname in question_names:
            bank_doc.append("questions", {"question_bank_question": qname})

        bank_doc.insert(ignore_permissions=True)

        frappe.db.set_value("Interview", interview_id, "custom_personalized_question_bank", bank_doc.name)
        frappe.db.commit()

        return str(bank_doc.name)
