import os
import json
import pytest
from pathlib import Path
from dotenv import load_dotenv
from pipeLine2.utils import resume_promt_summary

# Load .env to get the Gemini API key
dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))
load_dotenv(dotenv_path=dotenv_path)
GEMINI_KEY = os.getenv("GEMINI_API_KEY")


# Test the resume_promt_summary function
def test_resume_promt_summary():

    from dotenv import load_dotenv
    import os
    load_dotenv()

    if not os.getenv("GEMINI_API_KEY"):
        pytest.skip("Gemini API key not set")

    from dotenv import load_dotenv
    import os
    load_dotenv()

    if not os.getenv("GEMINI_API_KEY"):
        pytest.skip("Gemini API key not set")

    resume_dir = Path("resume")
    required_files = [
        "resume.json",
        "resume_updated.json",
        "job_posting.json"
    ]

    # Check that all required files exist
    for filename in required_files:
        assert (resume_dir / filename).exists(), f"{filename} is missing"

    # Optional: check if resume_user_answers.json exists and is valid
    user_answers_path = resume_dir / "resume_user_answers.json"
    if user_answers_path.exists():
        with open(user_answers_path, "r", encoding="utf-8") as f:
            user_answers = json.load(f)
            assert isinstance(user_answers, list)

    # Run the actual function (calls Gemini)
    resume_promt_summary()

    # Verify output file was created
    output_path = resume_dir / "resume_summary.json"
    assert output_path.exists(), "resume_summary.json was not created"

    # Check output structure
    with open(output_path, "r", encoding="utf-8") as f:
        result = json.load(f)

    assert "professional_summary" in result
    assert isinstance(result["professional_summary"], str)
    assert len(result["professional_summary"]) > 20  # sanity check

# Test the resume_education_info_personal function
from pipeLine2.utils import resume_education_info_personal

def test_resume_education_info_personal():
    resume_dir = Path("resume")
    input_path = resume_dir / "resume.json"
    output_path = resume_dir / "resume_education_info_personal.json"

    # Ensure the input file exists
    assert input_path.exists(), "resume.json not found. Please ensure it exists before testing."

    # Run the function
    resume_education_info_personal()

    # Check the output file was created
    assert output_path.exists(), "Expected output file was not created."

    # Load and validate the contents
    with open(output_path, "r", encoding="utf-8") as f:
        result = json.load(f)

    assert "personal_information" in result
    assert "education" in result
    assert isinstance(result["personal_information"], dict)
    assert isinstance(result["education"], list) or isinstance(result["education"], dict)

# Added this function since there was no function to extract the final experience in the utils.py file
def extract_final_experience():
    input_filepath = "resume/resume_updated.json"
    output_filepath = "resume/resume_final_experience.json"

    with open(input_filepath, "r", encoding="utf-8") as file:
        resume_data = json.load(file)

    experience = resume_data.get("work_experience", [])

    with open(output_filepath, "w", encoding="utf-8") as out:
        json.dump({"work_experience": experience}, out, indent=4, ensure_ascii=False)
        print(f"✅ Final experience saved to: {output_filepath}")
extract_final_experience()

# Test the join_all_resume_json function
from pipeLine2.utils import join_all_resume_json

def test_join_all_resume_json():
    resume_dir = Path("resume")

    # Input files required by the function
    required_files = [
        "resume_education_info_personal.json",
        "resume_summary.json",
        "resume_match_skills.json"
    ]

    for filename in required_files:
        path = resume_dir / filename
        assert path.exists(), f"{filename} is missing."

    # Optional file
    user_answers_path = resume_dir / "resume_user_answers.json"
    if user_answers_path.exists():
        with open(user_answers_path, "r", encoding="utf-8") as f:
            user_answers = json.load(f)
            assert isinstance(user_answers, list), "resume_user_answers.json should be a list of answers."

    # Run the function
    join_all_resume_json()

    # Validate final output file
    output_path = resume_dir / "resume_final_to_word.json"
    assert output_path.exists(), "resume_final_to_word.json was not created."

    # Validate contents
    with open(output_path, "r", encoding="utf-8") as f:
        final_resume = json.load(f)

    assert "education" in final_resume
    assert "personal_information" in final_resume
    assert "professional_summary" in final_resume
    assert "skills" in final_resume
    assert "work_experience" in final_resume

    assert isinstance(final_resume["skills"], list)
    assert len(final_resume["skills"]) > 0
