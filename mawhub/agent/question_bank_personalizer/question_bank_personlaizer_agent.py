import json
from google import genai
from google.genai import types

from mawhub.agent.question_bank_personalizer.instructions import PERSONALIZER_SYSTEM_INSTRUCTION
from mawhub.agent.question_bank_personalizer.types import (
    CandidateProfile,
    JobObjectives,
    PersonalizedQuestionBankModel,
    PersonalizedQuestionBankQuestion,
    QuestionBankQuestion,
)


class QuestionBankPersonalizerAgent:
    def __init__(self, client: genai.Client, model_name: str):
        self.client = client
        self.model_name = model_name

    def run(
        self,
        candidate: CandidateProfile,
        job_objectives: JobObjectives,
        original_questions: list[QuestionBankQuestion],
    ) -> list[PersonalizedQuestionBankQuestion]:
        """
        Receives candidate profile, job objectives, and the original question bank.
        Returns a personalized question bank ordered by relevance to the candidate.
        """
        prompt = (
            f"Candidate:\n{candidate.model_dump_json(indent=2)}\n\n"
            f"Job Objectives:\n{job_objectives.model_dump_json(indent=2)}\n\n"
            f"Questions:\n{json.dumps([q.model_dump() for q in original_questions], indent=2)}"
        )

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=PERSONALIZER_SYSTEM_INSTRUCTION,
                temperature=0.2,
                top_p=0.9,
                max_output_tokens=8000,
                response_mime_type="application/json",
                response_schema=PersonalizedQuestionBankModel,
            ),
        )

        if response.parsed is not None:
            result = PersonalizedQuestionBankModel.model_validate(response.parsed)
        else:
            raw = response.text or ""
            result = PersonalizedQuestionBankModel.model_validate(json.loads(raw))

        return result.questions
