import json
from google import genai
from google.genai import types

from mawhub.agent.question_bank_maker.instructions import MAKER_SYSTEM_INSTRUCTION
from mawhub.agent.question_bank_maker.types import GeneratedQuestionBankModel, JobInfo
from mawhub.agent.question_bank_personalizer.types import QuestionBankQuestion


class QuestionBankMakerAgent:
    def __init__(self, client: genai.Client, model_name: str):
        self.client = client
        self.model_name = model_name

    def run(self, job_info: JobInfo) -> list[QuestionBankQuestion]:
        """
        Receives job information only and generates a generic question bank
        suitable for any candidate applying to that role.
        """
        print(f"[QuestionBankMaker] Starting generation for role='{job_info.role_title}' seniority='{job_info.seniority_level}'")

        prompt = f"Job Information:\n{job_info.model_dump_json(indent=2)}"

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=MAKER_SYSTEM_INSTRUCTION,
                temperature=0.4,
                top_p=0.9,
                max_output_tokens=32000,
                response_mime_type="application/json",
                response_schema=GeneratedQuestionBankModel,
            ),
        )

        if response.parsed is not None:
            print("[QuestionBankMaker] Response received via structured output (parsed)")
            result = GeneratedQuestionBankModel.model_validate(response.parsed)
        else:
            print("[QuestionBankMaker] response.parsed is None — falling back to response.text")
            raw = response.text or ""
            print(f"[QuestionBankMaker] raw text length={len(raw)} chars")
            result = GeneratedQuestionBankModel.model_validate(json.loads(raw))

        print(f"[QuestionBankMaker] Generated {len(result.questions)} questions")
        return result.questions
