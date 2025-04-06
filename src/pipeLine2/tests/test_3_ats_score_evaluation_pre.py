import os
import json
import pytest
from pathlib import Path
from dotenv import load_dotenv
from pipeLine2.utils import ats_score_evaluation_pre

# Load .env to get the Gemini API key
dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))
load_dotenv(dotenv_path=dotenv_path)
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

def test_ats_score_evaluation_pre():

    from dotenv import load_dotenv
    import os
    load_dotenv()

    if not os.getenv("GEMINI_API_KEY"):
        pytest.skip("Gemini API key not set")
        
    resume_dir = Path("resume")
    resume_path = resume_dir / "resume.json"
    job_path = resume_dir / "job_posting.json"

    # Ensure required input files exist
    assert resume_path.exists(), "Missing resume.json"
    assert job_path.exists(), "Missing job_posting.json"

    # Run the real Gemini-based function
    ats_score_evaluation_pre()

    # Validate output file is created
    output_path = resume_dir / "ats_score_evaluation_pre.json"
    assert output_path.exists(), "Expected ATS output not found"

    # Validate file contents
    with open(output_path, "r", encoding="utf-8") as f:
        result = json.load(f)

    assert "ats_score" in result
    assert "matching_technical_skills" in result
    assert isinstance(result["ats_score"], int)
