import google.generativeai as genai
import PyPDF2
import re
from collections import Counter

# Configure Gemini API
API_KEY = "YOUR_API_KEY_HERE"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file."""
    text = ""
    with open(pdf_path, "rb") as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text

def analyze_with_gemini(resume_text, job_posting):
    """Uses Gemini to analyze the resume content and match it with a job posting."""
    prompt = (
        "Analyze the following resume text and evaluate its ATS score based on these criteria: "
        "\n - Detected sections (Education, Experience, Skills, Projects, Certifications)"
        "\n - Presence of tables and images"
        "\n - Usage of action verbs in a professional context"
        "\n - Match percentage with the provided job posting"
        "\n Calculate score and some recommendations."
        f"\n\nResume Text:\n{resume_text}"
        f"\n\nJob Posting:\n{job_posting}"
    )
    response = model.generate_content(prompt)
    return response.text

def calculate_ats_score(pdf_path, job_posting):
    """Calculates the ATS score using Gemini and matches the resume with the job posting."""
    resume_text = extract_text_from_pdf(pdf_path)
    analysis_result = analyze_with_gemini(resume_text, job_posting)
    return analysis_result

# Usage
document_path  = "D:\\Big Data\\Term 3\\1. Big Data Capstone Project\\Project\\AutoApply\\src\\resumes\\resume_sample_1.pdf"
job_posting_text = "Bachelor's degree in Computer Science, Information Technology, Business or equivalent; Strong overall data & analytics background; Minimum 7 years work experience providing business analysis with complex business processes and integrated systems; Minimum 5 years of end-to-end experience in implementing enterprise data warehouse and BI solutions; Minimum 7 years of experience with data discovery, data modeling, and data quality; Experience working within large enterprise organizations; Superior written and verbal communication skills and excellent facilitation skills to proactively engage multiple internal stakeholder groups."
ats_result = calculate_ats_score(document_path, job_posting_text)
print(ats_result)

# Reference: 
# (OpenAI first prompt, 2025): I am going to work with Gemini, and I need an agent to read a PDF resume and perform an ATS evaluation, with a score for that resume and recommendations.
# (OpenAI last prompt, 2025): The ATS also includes the match with a job posting that the user places