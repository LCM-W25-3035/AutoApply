import openai
import json
import streamlit as st
import pandas as pd
import google.generativeai as genai
from pypdf import PdfReader
from io import BytesIO
import numpy as np


your_api_key = "AIzaSyAAhEq8NyaV8t9IQjSHdF7XhgF69GQW95U"
model_gemini = "models/gemini-2.0-flash"
clean_json = "```json\n"

def extract_cv_information(uploaded_pdf):
    # Read the PDF content using pypdf
    pdf_reader = PdfReader(BytesIO(uploaded_pdf.getvalue()))
    pdf_text = ""
    for page in pdf_reader.pages:
        pdf_text += page.extract_text()

    system_instructions = """
    You are an HR analyst responsible for processing and analyzing resumes. Your task is to extract the following information from a given resume:

    1. Technical Skills:
        -Identify and list all technical skills explicitly mentioned in the resume.
        -These may include programming languages, frameworks, libraries, databases, cloud platforms, and relevant tools.
    2. Soft Skills:
        -Identify and list all soft skills mentioned in the resume.
        -Additionally, infer soft skills based on the candidate's experience, achievements, and responsibilities.
        -Examples include leadership, teamwork, adaptability, problem-solving, communication, critical thinking, and emotional intelligence.
    3. Years of Experience:
        -Calculate and provide the total number of years of professional experience.
    4. Education:
        -Extract and list all education details, including:
            -Degree
            -Institution
            -Location
            -Start date
            -End date
    5. Experience Level:
        -Determine the candidate's highest level of experience based on job roles, industries, and responsibilities.
    6. Work Experience:
        -Extract all previous job positions and structure them as a list of dictionaries, where each dictionary represents a job.
        -Each dictionary must contain:
            -Job title
            -Company
            -Location
            -Start date
            -End date
            -Achievements and responsibilities associated with that role
    7. Professional Summary:
        -Extract the professional summary from the resume.
    8. Languages & Proficiency (Optional: If not found, omit this section):
        -Identify all languages spoken by the candidate and their proficiency level.
        -If no language information is found, exclude this section from the final JSON.
    9. Certifications (Optional: If not found, omit this section):
        -List all certifications the candidate has obtained, including:
        -Certification name
        -Issuing organization
        -Year issued
        -If no certifications are found, exclude this section from the final JSON.
    10. Personal information:
        -Name
        -Phone
        -Email
        -Addres
        -Identify and list Social media links

    11. Output Format:
        -Return only the JSON response in the exact structure below.
        -Do not include any explanations, extra text, or formatting beyond the JSON itself.

        {
        "technical_skills": [A],
        "soft_skills": [B],
        "years_of_experience": C,
        "education": [
            {
            "degree": D,
            "institution": D,
            "location": D,
            "start_date":D, 
            "end_date":D 
            }
        ],
        "experience_level": E,
        "work_experience": [
            {
            "job_title":F ,
            "company": F,
            "location": F,
            "start_date":F,
            "end_date":F ,
            "achievement": [F
            ]
            }
        ],
        "professional_summary": G,
        "languages": [
            {
            "language": H,
            "proficiency": H
            }
        ],
        "certifications": [
            {
            "name": I,
            "issuing_organization":I,
            "year_issued": I
            }
        ],
        "personal_information":{
            "name": J,
            "phone": J,
            "email": J,
            "addres": J,
            "social_media":[J]
        }
        }
    """

    genai.configure(api_key = your_api_key)
    model = genai.GenerativeModel(
    model_gemini,
    system_instruction=system_instructions,
    )

    response = model.generate_content(f"The resume to analyze is {pdf_text}")
    cleaned_response = response.text.strip(clean_json).strip("```").replace("\n", "")

    json_file = json.loads(cleaned_response)
    # Save the result to the output file
    output_filepath = "resume/resume.json"
    with open(output_filepath, "w", encoding="utf-8") as file_save:
        json.dump(json_file, file_save, ensure_ascii=False, indent=4)
        print(f"Output saved to '{output_filepath}'.")

def extract_job_posting_information(uploaded_job):
    # Read the PDF content using pypdf
    pdf_reader = PdfReader(BytesIO(uploaded_job.getvalue()))
    pdf_text = ""
    for page in pdf_reader.pages:
        pdf_text += page.extract_text()

    system_instructions = """
    You are a job market analyst specializing in processing and analyzing job postings. 
    Your task is to extract key information from a given job listing and structure it into a JSON format. 
    The extracted data should include:

    1. Job Information:
        -The job title of the position.
    2. Company Information:
        -The company name offering the position.
        -The industry in which the company operates.
        -The location where the job is based.
        -Whether the job is remote-friendly (true/false).
    3. Employment Type & Experience Level:
        -The employment type (e.g., Full-time, Part-time, Contract, Internship).
        -The experience level required (e.g., Junior, Mid, Senior, Lead).
        -The minimum years of experience required.
    4. Salary Information:
        -The salary range (minimum and maximum salary).
        -The currency in which the salary is offered.
        -The payment frequency (e.g., Hourly, Monthly, Annual).
    5. Job Description:
        -A short summary of the job description provided in the job posting.
    6. Responsibilities:
        -A list of job responsibilities as mentioned in the posting.
    7. Requirements:
        -A list of all mandatory job requirements specified in the posting.
    8. Skills Required:
        -Identify and list all technical skills required for the job.
        -Identify and list all soft skills required or implied in the posting.
    9. Education & Certifications (Optional: If not found, omit these sections):
        -Identify the minimum education level required (degree and field of study).
        -List any preferred institutions mentioned in the job description.
        -Identify any required certifications, including the certification name and issuing organization.
    10. Language Requirements (Optional: If not found, omit this section):
        -Identify all languages required for the job, along with the proficiency level.
    11. Benefits & Perks (Optional: If not found, omit this section):
        -Extract and list all benefits mentioned in the job posting (e.g., health insurance, remote work, bonuses, flexible hours).
    12. Application Information:
        -The application deadline (if provided).
        -The job posting date (if available).
        -The official application link where candidates can apply.

    13. Output Format:
        -Return ONLY the JSON response in the exact structure below.
        -Do NOT include any explanations, comments, or extra text beyond the JSON itself.

        {
        "job_title": "A",
        "company": {
            "name": "B",
            "industry": "C",
            "location": "D",
            "remote": E
        },
        "employment_type": "F",
        "experience_level": "G",
        "years_of_experience_required": H,
        "salary_range": {
            "min": I,
            "max": J,
            "currency": "K",
            "payment_frequency": "L"
        },
        "job_description": "M",
        "responsibilities": [
            "N"
        ],
        "requirements": [
            "O"
        ],
        "technical_skills": [
            "P"
        ],
        "soft_skills": [
            "Q"
        ],
        "education_required": [
            {
            "degree": "R",
            "field_of_study": "S",
            "preferred_institutions": ["T"]
            }
        ],
        "certifications_required": [
            {
            "name": "U",
            "issuing_organization": "V"
            }
        ],
        "languages_required": [
            {
            "language": "W",
            "proficiency": "X"
            }
        ],
        "benefits": [
            "Y"
        ],
        "application_deadline": "Z",
        "job_posting_date": "AA",
        "application_link": "BB"
        }
    """

    genai.configure(api_key = your_api_key)
    model = genai.GenerativeModel(
    model_gemini,
    system_instruction=system_instructions,
    )

    response = model.generate_content(f"The job posting to analyze is {pdf_text}")
    cleaned_response = response.text.strip(clean_json).strip("```").replace("\n", "")

    json_file = json.loads(cleaned_response)
    # Save the result to the output file
    output_filepath = "resume/job_posting.json"
    with open(output_filepath, "w", encoding="utf-8") as file_save:
        json.dump(json_file, file_save, ensure_ascii=False, indent=4)
        print(f"Output saved to '{output_filepath}'.")



def extract_job_posting_information_from_str(uploaded_job):

    pdf_text = uploaded_job

    system_instructions = """
    You are a job market analyst specializing in processing and analyzing job postings. 
    Your task is to extract key information from a given job listing and structure it into a JSON format. 
    The extracted data should include:

    1. Job Information:
        -The job title of the position.
    2. Company Information:
        -The company name offering the position.
        -The industry in which the company operates.
        -The location where the job is based.
        -Whether the job is remote-friendly (true/false).
    3. Employment Type & Experience Level:
        -The employment type (e.g., Full-time, Part-time, Contract, Internship).
        -The experience level required (e.g., Junior, Mid, Senior, Lead).
        -The minimum years of experience required.
    4. Salary Information:
        -The salary range (minimum and maximum salary).
        -The currency in which the salary is offered.
        -The payment frequency (e.g., Hourly, Monthly, Annual).
    5. Job Description:
        -A short summary of the job description provided in the job posting.
    6. Responsibilities:
        -A list of job responsibilities as mentioned in the posting.
    7. Requirements:
        -A list of all mandatory job requirements specified in the posting.
    8. Skills Required:
        -Identify and list all technical skills required for the job.
        -Identify and list all soft skills required or implied in the posting.
    9. Education & Certifications (Optional: If not found, omit these sections):
        -Identify the minimum education level required (degree and field of study).
        -List any preferred institutions mentioned in the job description.
        -Identify any required certifications, including the certification name and issuing organization.
    10. Language Requirements (Optional: If not found, omit this section):
        -Identify all languages required for the job, along with the proficiency level.
    11. Benefits & Perks (Optional: If not found, omit this section):
        -Extract and list all benefits mentioned in the job posting (e.g., health insurance, remote work, bonuses, flexible hours).
    12. Application Information:
        -The application deadline (if provided).
        -The job posting date (if available).
        -The official application link where candidates can apply.

    13. Output Format:
        -Return ONLY the JSON response in the exact structure below.
        -Do NOT include any explanations, comments, or extra text beyond the JSON itself.

        {
        "job_title": "A",
        "company": {
            "name": "B",
            "industry": "C",
            "location": "D",
            "remote": E
        },
        "employment_type": "F",
        "experience_level": "G",
        "years_of_experience_required": H,
        "salary_range": {
            "min": I,
            "max": J,
            "currency": "K",
            "payment_frequency": "L"
        },
        "job_description": "M",
        "responsibilities": [
            "N"
        ],
        "requirements": [
            "O"
        ],
        "technical_skills": [
            "P"
        ],
        "soft_skills": [
            "Q"
        ],
        "education_required": [
            {
            "degree": "R",
            "field_of_study": "S",
            "preferred_institutions": ["T"]
            }
        ],
        "certifications_required": [
            {
            "name": "U",
            "issuing_organization": "V"
            }
        ],
        "languages_required": [
            {
            "language": "W",
            "proficiency": "X"
            }
        ],
        "benefits": [
            "Y"
        ],
        "application_deadline": "Z",
        "job_posting_date": "AA",
        "application_link": "BB"
        }
    """

    genai.configure(api_key = your_api_key)
    model = genai.GenerativeModel(
    model_gemini,
    system_instruction=system_instructions,
    )

    response = model.generate_content(f"The job posting to analyze is {pdf_text}")
    cleaned_response = response.text.strip(clean_json).strip("```").replace("\n", "")

    json_file = json.loads(cleaned_response)
    # Save the result to the output file
    output_filepath = "resume/job_posting.json"
    with open(output_filepath, "w", encoding="utf-8") as file_save:
        json.dump(json_file, file_save, ensure_ascii=False, indent=4)
        print(f"Output saved to '{output_filepath}'.")



def find_best_jobs(cv_file, job_offers):
    """Finds the top 10 best matching jobs using cosine similarity."""
    cv_text = extract_text_from_file(cv_file)
    
    job_texts = [job['Description'] for job in job_offers]
    job_titles = [job['Title'] for job in job_offers]
    
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform([cv_text] + job_texts)
    
    similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
    best_matches_idx = similarities.argsort()[-10:][::-1]
    
    best_jobs = [
        {"Title": job_titles[i], "Similarity": similarities[i]} 
        for i in best_matches_idx
    ]
    
    return pd.DataFrame(best_jobs)


def skills_missing():
    # Extract skills from resume and job posting
    cv_skills = set(cv_data.get("technical_skills", []))
    job_skills = set(job_data.get("technical_skills", []))

    # Identify missing skills (limit to 5)
    missing_skills = list(job_skills - cv_skills)[:5]

    for skill in missing_skills:
        print(f"Do you have experience with {skill}? (yes/no)")
        answer = input("Your answer: ").strip().lower()

        if answer == "yes":
            while True:
                # Ask the user to describe their experience with the skill
                detail = input(f"Describe your experience with {skill}, including how you obtained it and a metric or result achieved: ")

                # Validate the response with Gemini
                validation_prompt = (
                    f"Evaluate the following response regarding experience with {skill}. "
                    f"Ensure it includes:\n"
                    f"- A clear explanation of how the experience was obtained.\n"
                    f"- At least one action verb describing what was done.\n"
                    f"- A quantifiable metric or measurable impact.\n\n"
                    f"Response to evaluate:\n{detail}\n\n"
                    f"### Evaluation Criteria ###\n"
                    f"- If the response meets all criteria, return: 'Evaluation: ✅ Strong response.'\n"
                    f"- If the response is missing details, return: 'Evaluation: ❌ Needs improvement.' "
                    f"and provide a suggestion with an example of how the response should be structured.\n\n"
                    f"### Example of a strong response ###\n"
                    f"'Implemented a predictive maintenance system using Python, reducing machine downtime by 25% over six months.'\n\n"
                )

                try:
                    response = model.generate_content(validation_prompt)
                    feedback = response.text.strip()
                    print("\n🔹 Gemini Response:\n", feedback)  # Display Gemini's response for debugging

                    # If the response is strong, save it and exit the loop
                    if re.search(r"✅ Strong response", feedback, re.IGNORECASE):
                        save_answers[skill] = detail
                        break

                    # If the response needs improvement, show feedback and an example
                    if re.search(r"❌ Needs improvement", feedback, re.IGNORECASE):
                        print("\n⚠️ Your answer needs improvement.")

                        # Extract a strong response example from Gemini's feedback
                        example_match = re.search(r"Example of a strong response:\s*(.+)", feedback, re.IGNORECASE)
                        if example_match:
                            print(f"\n🔄 Example of how you should structure your answer:\n{example_match.group(1).strip()}")

                        print("\nPlease try again with more detail using action verbs and metrics.")

                except Exception as e:
                    print(f"\n❌ Error communicating with Gemini: {e}")
                    print("Skipping this skill...")
                    break

    # Save responses to a JSON file
    with open("user_answers.json", "w") as file:
        json.dump(save_answers, file, indent=4)

    print("\n✅ Answers saved successfully.")



""" First Prompt in chatgpt
I need that when a resume in PDF format is read, a .json file is generated that can be recreated as best as possible. I want them to be {{
      "technical_skills": [A],
      "soft_skills": [B],
      "years_of_experience": C,
      "education": [
       {{
       "name": "",
       "place": "D",}}
       ],
       "experience_level": "E",
       "key_achievements": [
       {{
        "achievement": "F",
        "context": "F"
        }}
        ],
        "domain_expertise": [G],
        "job_titles": [H],  
        "industries": [I],
        "professional_summary": "J"
        }}
"""

""" Last Prompt in chatgpt
You are an HR analyst and you receive resumes and must analyze them to answer:
A. Identify and list all ***hard skills*** (e.g., programming languages, frameworks, libraries, databases, cloud platforms, and tools) explicitly mentioned in the resume.
B. Identify and list all ***soft skills*** (e.g., leadership, teamwork, adaptability, problem solving, communication, critical thinking, emotional intelligence) found in the resume and that you can also infer from the resume.
C. How many years of total professional experience does the candidate have?
D. Identify and list all educational information, degree, institution, location, start date, end date
E. What is the candidate's highest level of experience based on job roles, industries, and responsibilities?
F. Identify and list all of the candidate's work experience candidate:
- A list of dictionaries where in each dictionary there is a job that the candidate had.
- The dictionary should have the job title, company, location, start date, end date and all the achievements or responsibilities that the CV has in that particular position.
- The same information for all jobs
G. Find the professional summary.
H. All languages ​​and skills, if you don't find them in the candidate ignore and delete this section
I. All certifications that the candidate has, if you don't find them delete this section
J. Find the professional summary.

Returns only the JSON response in the exact structure shown below, without explanations or additional text:

{
"technical_skills": [A],
"soft_skills": [B],
"years_of_experience": C,
"education": [
{
"degree": D,
"institution": D,
"location": D,
"start_date":D,
"end_date":D
}
],
"experience_level": E,
"work_experience": [
{
"job_title":F ,
"company": F,
"location": F,
"start_date":F,
"end_date":F ,
"achievement": [F
]
}
],
"professional_summary": G,
"languages": [
{
"language": H,
"proficiency": H
}
],
"certifications": [
{
"name": I,
"issuing_organization": I,
"issuing_year": I
}
]
}"
"""