from typing import Dict, Any
from base_agent import BaseAgent
import json

class AnalyzerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Analyzer",
            instructions="""Analyze candidate profiles and extract:
            1. Technical skills (as a list)
            2. Years of experience (numeric)
            3. Education level
            4. Experience level (Junior/Mid-level/Senior)
            5. Key achievements
            6. Domain expertise
            
            Format the output as structured JSON data.""",
        )

    async def run(self, messages: list) -> Dict[str, Any]:
        """Analyze the extracted resume data"""
        print("🔍 Analyzer: Analyzing candidate profile")

        extracted_data = messages[-1]["content"]  # No eval() needed

        # Ensure structured data exists
        if "structured_data" not in extracted_data:
            print("❌ Error: Missing 'structured_data' key in input.")
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
            "domain_expertise": []
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
            }

        return {
            "skills_analysis": parsed_results,
            "analysis_timestamp": "2025-02-02",
            "confidence_score": 0.85 if "error" not in parsed_results else 0.5,
        }
