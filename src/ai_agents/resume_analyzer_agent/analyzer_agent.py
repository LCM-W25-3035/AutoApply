from typing import Dict, Any
import json
from openai import OpenAI
from datetime import datetime

class AnalyzerAgent:
    def __init__(self):
        self.name = "Analyzer"
        self.instructions = """Analyze candidate profiles and extract:
        1. Technical skills (as a list)
        2. Years of experience (numeric)
        3. Education level
        4. Experience level (Junior/Mid-level/Senior)
        5. Key achievements
        6. Domain expertise
        7. Job titles
        8. Industries
        9. Professional summary

        Format the output as structured JSON data."""

        # Ollama API Client
        self.ollama_client = OpenAI(
            base_url="http://localhost:11434/v1",
            api_key="ollama",  # required but unused
        )

    async def run(self, messages: list) -> Dict[str, Any]:
        """Analyze the extracted resume data"""
        print("🔍 Analyzer: Analyzing candidate profile")

        extracted_data = messages[-1]["content"]

        # Ensure structured data exists
        if "structured_data" not in extracted_data:
            print("Error: Missing 'structured_data' key in input.")
            return {"error": "Missing structured_data in input"}

        structured_data = extracted_data["structured_data"]

        # Generate analysis prompt for Ollama
        analysis_prompt = f"""
        Analyze this structured resume data and return a JSON object with the following structure:
        {{
            "technical_skills": {{"categories": {{}}, "other_skills": []}},
            "years_of_experience": 0,
            "education": {{"level": "Unknown", "field": "Unknown"}},
            "experience_level": "Junior",
            "key_achievements": [],
            "domain_expertise": [],
            "job_titles": [],  
            "industries": [],
            "professional_summary": ""
        }}

        Resume data:
        {structured_data}

        Only return the JSON object without any explanations or extra text.
        """

        # Query Ollama
        analysis_results = self._query_ollama(analysis_prompt)
        parsed_results = self._parse_json_safely(analysis_results)

        # Ensure we have valid data even if parsing fails
        if "error" in parsed_results:
            parsed_results = {
                "technical_skills": {"categories": {}, "other_skills": []},
                "years_of_experience": 0,
                "education": {"level": "Unknown", "field": "Unknown"},
                "experience_level": "Junior",
                "key_achievements": [],
                "domain_expertise": [],
                "job_titles": [],  
                "industries": [],
                "professional_summary": "",
            }

        return {
            "skills_analysis": parsed_results,
            "analysis_timestamp": datetime.today().strftime("%Y-%m-%d")
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