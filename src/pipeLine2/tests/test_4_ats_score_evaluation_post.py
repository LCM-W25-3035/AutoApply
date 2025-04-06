import os
import json
import pytest
from pathlib import Path
from dotenv import load_dotenv
from pipeLine2.utils import ats_score_evaluation_post

# Load .env to get the Gemini API key
dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))
load_dotenv(dotenv_path=dotenv_path)
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

@pytest.mark.skipif(not GEMINI_KEY, reason="Gemini API key not set")
def test_ats_score_evaluation_post_with_real_files():
    resume_dir = Path("resume")

    required_files = [
        "resume_final_to_word.json",
        "ats_score_evaluation_pre.json",
        "job_posting.json"
    ]

    # ✅ Ensure all required files exist
    for file_name in required_files:
        file_path = resume_dir / file_name
        assert file_path.exists(), f"Required input file missing: {file_name}"

    # ✅ Run the real function (calls Gemini)
    ats_score_evaluation_post()

    # ✅ Check output file
    output_path = resume_dir / "ats_score_evaluation_post.json"
    assert output_path.exists(), "Output file ats_score_evaluation_post.json was not created."

    # ✅ Validate structure of output
    with open(output_path, "r", encoding="utf-8") as f:
        result = json.load(f)

    required_keys = [
        "ats_score",
        "matching_technical_skills",
        "missing_technical_skills",
        "matching_soft_skills",
        "missing_soft_skills",
        "keywords_matched",
        "keywords_missing",
        "years_of_experience_match",
        "education_match",
        "summary_match",
        "responsibility_alignment",
        "recommendations"
    ]

    for key in required_keys:
        assert key in result, f"Missing expected key in result: {key}"

    assert isinstance(result["ats_score"], int)
    assert isinstance(result["recommendations"], list)
