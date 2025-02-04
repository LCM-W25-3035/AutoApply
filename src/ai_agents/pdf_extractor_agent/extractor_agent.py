from typing import Dict, Any
import json
from pdfminer.high_level import extract_text  # pip install pdfminer.six
from openai import OpenAI

class ExtractorAgent:
    def __init__(self):
        self.name = "Extractor"
        self.instructions = """Extract and structure information from resumes.
        Focus on: profile, professional summary, personal info, work experience, education, skills, domains, achievements and certifications.
        Provide output in a clear, structured format."""

        # Ollama API Client
        self.ollama_client = OpenAI(
            base_url="http://localhost:11434/v1",
            api_key="ollama",  # required but unused
        )

    async def run(self, messages: list) -> Dict[str, Any]:
        """Process the resume and extract information"""
        print("Extractor: Processing resume")

        resume_data = messages[-1]["content"]

        # Extract text from PDF
        if resume_data.get("file_path"):
            raw_text = extract_text(resume_data["file_path"])
        else:
            raw_text = resume_data.get("text", "")

        # Get structured information from Ollama
        extracted_info = self._query_ollama(raw_text)

        return {
            "raw_text": raw_text,
            "structured_data": extracted_info,
            "extraction_status": "completed",
        }

    def _query_ollama(self, prompt: str) -> str:
        """Query Ollama model with the given prompt"""
        try:
            response = self.ollama_client.chat.completions.create(
                model="llama3.2",  # Updated to llama3.2
                messages=[
                    {"role": "system", "content": self.instructions},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=2000,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error querying Ollama: {str(e)}")
            raise

    def _parse_json_safely(self, text: str) -> Dict[str, Any]:
        """Safely parse JSON from text, handling potential errors"""
        try:
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1:
                json_str = text[start : end + 1]
                return json.loads(json_str)
            return {"error": "No JSON content found"}
        except json.JSONDecodeError:
            return {"error": "Invalid JSON content"}
