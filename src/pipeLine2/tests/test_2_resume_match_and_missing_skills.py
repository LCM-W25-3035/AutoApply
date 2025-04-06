import os
import json
import pytest
from pathlib import Path
from pipeLine2.utils import resume_skills

def test_resume_skills_with_existing_json_files():
    resume_dir = Path("resume")
    input_resume = resume_dir / "resume.json"
    input_job = resume_dir / "job_posting.json"
    output_missing = resume_dir / "resume_missing_skills.json"
    output_match = resume_dir / "resume_match_skills.json"

    # Pre-check: Ensure required input files exist
    assert input_resume.exists(), "resume.json is missing."
    assert input_job.exists(), "job_posting.json is missing."

    # Run the function
    resume_skills()

    # Check both output files were created
    assert output_missing.exists(), "Missing skills file was not created."
    assert output_match.exists(), "Match skills file was not created."

    # Validate missing skills content
    with open(output_missing, "r", encoding="utf-8") as f:
        missing = json.load(f)
    assert "technical_skills" in missing
    assert "soft_skills" in missing
    assert isinstance(missing["technical_skills"], list)
    assert isinstance(missing["soft_skills"], list)

    # Validate match skills content
    with open(output_match, "r", encoding="utf-8") as f:
        match = json.load(f)
    assert "technical_skills" in match
    assert "soft_skills" in match
    assert isinstance(match["technical_skills"], list)
    assert isinstance(match["soft_skills"], list)
