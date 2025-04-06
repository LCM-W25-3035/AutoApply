import os
import json
import pytest
from pathlib import Path
from pipeLine2.utils import generate_cv

def test_generate_cv_creates_docx():
    # Input paths
    input_json = Path("resume/resume_final_to_word.json")
    template_path = Path("template/template1.docx")

    # Pre-check: Make sure required files exist
    assert input_json.exists(), "resume_final_to_word.json is missing."
    assert template_path.exists(), "Word template file is missing."

    # Read user name from input
    with open(input_json, "r", encoding="utf-8") as f:
        resume_data = json.load(f)
    user_name = resume_data.get("personal_information", {}).get("name", "Unknown").strip()
    user_name = " ".join(user_name.title().split())

    expected_output_path = Path(f"output/{user_name}_customization.docx")

    # Run the generator
    result = generate_cv()

    assert result is True, "generate_cv() should return True on success"
    assert expected_output_path.exists(), f"Expected output file not found: {expected_output_path}"
