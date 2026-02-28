from google.genai import types, Client
from .instructions import EXTRACT_FILE_TEXT_SYSTEM_INSTRUCTION, EXTRACT_FILE_TEXT_USER_PROMPT

from mawhub.pkg.pdfconvertor.pdfconvertor import read_file_data

class FileTextParserWorkflow:
    """
    Agent to extract text from a file (currently PDFs supported).
    """

    def __init__(
            self,
             client: Client,
             model_name: str,
     ):
        self.client = client
        self.default_model = model_name


    def run(self, file_path: str) -> str:
        """
        Reads the file using read_file() and returns text.
        Supports PDFs and plain text files.
        """
        parts = [types.Part.from_text(text=EXTRACT_FILE_TEXT_USER_PROMPT)]

        file_data = read_file_data(file_path)
        pdf_bytes = file_data.get("file_bytes")
        file_type = file_data.get("file_type")
        # pdf_bytes = read_pdf_bytes(file_path)
        # If file path provided → attach file
        if pdf_bytes:
            parts.append(
                types.Part.from_bytes(
                    data=pdf_bytes,
                    mime_type=file_type,
                )
            )

        try:
            response = self.client.models.generate_content(
                model=self.default_model,
                contents=types.Content(
                    role="user",
                    parts=parts
                    ),
                config=types.GenerateContentConfig(
                    system_instruction=EXTRACT_FILE_TEXT_SYSTEM_INSTRUCTION,
                    temperature=0,
                    )
                )
            return response.text or ""

        except Exception as e:
            raise ValueError(f"LLM output could not be parsed as JobOpening: {str(e)}")
