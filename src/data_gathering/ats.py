import google.generativeai as genai
from dotenv import load_dotenv
import os
import json


load_dotenv()
# Configure Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')


def format_prompt(resume_json, job_json):
    resume_skills = ", ".join(resume_json.get("technical_skills", []))
    resume_soft_skills = ", ".join(resume_json.get("soft_skills", []))
    resume_summary = resume_json.get("professional_summary", "")
    resume_experience = "\n".join([
        f"- {exp['job_title']} at {exp['company']} ({exp['start_date']} to {exp['end_date']})\n  Achievements: {'; '.join(exp['achievement'])}"
        for exp in resume_json.get("work_experience", [])
    ])

    job_title = job_json.get("job_title", "")
    job_summary = job_json.get("job_description", "")
    job_tech_skills = ", ".join(job_json.get("technical_skills", []))
    job_soft_skills = ", ".join(job_json.get("soft_skills", []))
    job_requirements = "\n".join(job_json.get("requirements", []))

    prompt = f"""
            You are an expert HR ATS evaluation agent. Score the following resume against the job posting.
            Evaluate based on:
            1. Skill match (technical & soft skills)
            2. Experience relevance and years
            3. Job responsibilities and resume alignment
            4. Professional Summary match
            5. Recommendations for better alignment

            Return output in JSON format:
            {{
            "ats_score": <0-100>,
            "matching_skills": [list],
            "missing_skills": [list],
            "matching_soft_skills": [list],
            "missing_soft_skills": [list],
            "years_of_experience_match": "Yes/No",
            "recommendations": [list]
            }}

            ===== JOB POSTING =====
            Job Title: {job_title}
            Summary: {job_summary}
            Required Skills: {job_tech_skills}
            Required Soft Skills: {job_soft_skills}
            Requirements:
            {job_requirements}

            ===== RESUME =====
            Summary: {resume_summary}
            Experience:
            {resume_experience}

            Technical Skills: {resume_skills}
            Soft Skills: {resume_soft_skills}
            """
    return prompt



def ATS_Score(resume_json, job_json):
    prompt = format_prompt(resume_json, job_json)
    response = model.generate_content(prompt)
    return response.text


with open('resume.json') as r, open('job_posting_0.json') as j:
    resume = json.load(r)
    job = json.load(j)

result = ATS_Score(resume, job)
print(result)
