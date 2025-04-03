import unittest
import json
import os
from unittest.mock import patch, mock_open

from pipeLine2.utils import ats_score_evaluation_pre, ats_score_evaluation_post

class TestATSScoring(unittest.TestCase):

    def setUp(self):
        # Mocked resume.json
        self.mock_resume = {
            "personal_information": {"name": "Test User"},
            "professional_summary": "Experienced data scientist.",
            "technical_skills": ["Python", "TensorFlow", "SQL"],
            "soft_skills": ["Teamwork", "Communication"],
            "education": [{"degree": "B.Sc Computer Science", "institution": "XYZ University"}],
            "work_experience": [{"job_title": "Data Scientist", "company": "TechCorp"}],
            "years_of_experience": 3
        }

        # Mocked job_posting.json
        self.mock_job_posting = {
            "job_title": "Machine Learning Engineer",
            "job_description": "Looking for a candidate with Python and TensorFlow experience.",
            "technical_skills": ["Python", "TensorFlow", "Kubernetes"],
            "soft_skills": ["Teamwork", "Problem Solving"],
            "years_of_experience_required": 2,
            "requirements": ["Bachelor’s degree in CS"],
            "responsibilities": ["Build ML models", "Collaborate with data engineers"]
        }

        # Mocked ATS pre-score output
        self.mock_ats_pre = {
            "matching_technical_skills": ["Python", "TensorFlow"],
            "missing_technical_skills": ["Kubernetes"],
            "matching_soft_skills": ["Teamwork"],
            "missing_soft_skills": ["Problem Solving"],
            "keywords_matched": ["Python", "TensorFlow"],
            "keywords_missing": ["Kubernetes"],
            "ats_score": 80,
            "years_of_experience_match": "Yes",
            "education_match": "Yes",
            "summary_match": "Strong",
            "responsibility_alignment": "Partial",
            "recommendations": ["Add more details about Kubernetes."]
        }

        # Write all mocks to actual test files
        os.makedirs("resume", exist_ok=True)
        with open("resume/resume.json", "w", encoding="utf-8") as f:
            json.dump(self.mock_resume, f)
        with open("resume/job_posting.json", "w", encoding="utf-8") as f:
            json.dump(self.mock_job_posting, f)
        with open("resume/ats_score_evaluation_pre.json", "w", encoding="utf-8") as f:
            json.dump(self.mock_ats_pre, f)
        with open("resume/resume_final_to_word.json", "w", encoding="utf-8") as f:
            json.dump(self.mock_resume, f)

    @patch("pipeLine2.utils.genai.GenerativeModel.generate_content")
    def test_ats_score_evaluation_pre(self, mock_generate):
        # Simulate Gemini's JSON response
        mock_generate.return_value.text = json.dumps(self.mock_ats_pre)

        ats_score_evaluation_pre()

        with open("resume/ats_score_evaluation_pre.json", "r", encoding="utf-8") as f:
            result = json.load(f)

        self.assertEqual(result["ats_score"], 80)
        self.assertIn("Python", result["matching_technical_skills"])

    @patch("pipeLine2.utils.genai.GenerativeModel.generate_content")
    def test_ats_score_evaluation_post(self, mock_generate):
        # Simulate Gemini's JSON response for post-check
        mock_generate.return_value.text = json.dumps(self.mock_ats_pre)

        ats_score_evaluation_post()

        with open("resume/ats_score_evaluation_post.json", "r", encoding="utf-8") as f:
            result = json.load(f)

        self.assertEqual(result["ats_score"], 80)
        self.assertIn("Kubernetes", result["missing_technical_skills"])

    def tearDown(self):
        # Clean up test files
        for file in [
            "resume/resume.json",
            "resume/job_posting.json",
            "resume/ats_score_evaluation_pre.json",
            "resume/ats_score_evaluation_post.json",
            "resume/resume_final_to_word.json"
        ]:
            if os.path.exists(file):
                os.remove(file)

if __name__ == "__main__":
    unittest.main()
