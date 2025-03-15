import openai
import json
import streamlit as st
import pandas as pd
import google.generativeai as genai
from pypdf import PdfReader
from io import BytesIO
import numpy as np


your_api_key = ""

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

    10. Output Format:
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
        ]
        }
    """

    genai.configure(api_key = your_api_key)
    model = genai.GenerativeModel(
    "models/gemini-2.0-flash",
    system_instruction=system_instructions,
    )

    response = model.generate_content(f"The resume to analyze is {pdf_text}")
    cleaned_response = response.text.strip("```json\n").strip("```").replace("\n", "")
    st.write(f"Output Gemini: {cleaned_response}")

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
    "models/gemini-2.0-flash",
    system_instruction=system_instructions,
    )

    response = model.generate_content(f"The job posting to analyze is {pdf_text}")
    cleaned_response = response.text.strip("```json\n").strip("```").replace("\n", "")
    st.write(f"Output Gemini: {cleaned_response}")

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

import json

def resume_skills():
    # Specify the path of the file to be read
    input_filepath = "resume/resume.json"

    with open(input_filepath, "r", encoding="utf-8") as file_load:
       cv_data = json.load(file_load)

    # Specify the path of the file to be read
    input_filepath = "resume/job_posting.json"

    with open(input_filepath, "r", encoding="utf-8") as file_load:
       job_data = json.load(file_load)

    # Extract skills from the resume and job posting
    cv_technical_skills = set(cv_data.get("technical_skills", []))
    job_technical_skills = set(job_data.get("technical_skills", []))

    cv_soft_skills = set(cv_data.get("soft_skills", []))
    job_soft_skills = set(job_data.get("soft_skills", []))

    # Skills that are **in the job posting** but **not in the resume**
    missing_technical_skills = list(job_technical_skills - cv_technical_skills)[:5]
    missing_soft_skills = list(job_soft_skills - cv_soft_skills)[:5]

    # Skills that are **in both** the job posting and the resume
    match_technical_skills = list(cv_technical_skills & job_technical_skills)
    match_soft_skills = list(cv_soft_skills & job_soft_skills)

    # Create a JSON file with missing skills
    missing_skills = {
        "technical_skills": missing_technical_skills,
        "soft_skills": missing_soft_skills
    }

    # Create a JSON file with matching skills
    match_skills = {
        "technical_skills": match_technical_skills,
        "soft_skills": match_soft_skills
    }

    # Save missing skills to a JSON file
    with open("resume/resume_missing_skills.json", "w") as file:
        json.dump(missing_skills, file, indent=4)
    print("Missing skills saved in 'resume/resume_missing_skills.json'.")

    # Save matching skills to a JSON file
    with open("resume/resume_match_skills.json", "w") as file:
        json.dump(match_skills, file, indent=4)
    print("Skills missing saved in 'resume/resume_match_skills.json'.")

def resume_delete_experience_not_related():
    #Specify the path of the file you want to read
    input_filepath = f"resume/resume.json"

    with open(input_filepath, "r", encoding="utf-8") as file_load:
       resume = json.load(file_load)
    
    job_experience = {"work_experience":resume.get("work_experience", {})}
    
    # Specify the path of the file you want to read
    input_filepath = f"resume/job_posting.json"
    with open(input_filepath, "r", encoding="utf-8") as file_load:
       job_offer = json.load(file_load)
    
    system_instructions = """
    You are an HR specialist skilled in processing and analyzing resumes. Your task is to analyze each achievement in the work experience section and remove those that are not relevant to the given job offer.

    **Instructions:**
    - Use only the information available in the resume. Do not infer or add any details that are not explicitly mentioned.
    - Evaluate each achievement individually and determine if the experience and skills it describes align with the job posting.
    - Remove achievements that are not relevant to the job offer.
    - Maintain the original JSON format, ensuring that only the non-relevant achievements are removed.
    - Do not provide any explanations or extra text, only return the modified JSON.

    **Output Format:**
    (Same as input, but with non-relevant achievements removed)
    """

    genai.configure(api_key = your_api_key)
    model = genai.GenerativeModel(
    model_gemini,
    system_instruction=system_instructions,
    )

    response = model.generate_content(f"The work experience seccion to analyze is {job_experience} and the job offer is {job_offer}")
    cleaned_response = response.text.strip(clean_json).strip("```").replace("\n", "")
    print(cleaned_response)
    json_file = json.loads(cleaned_response)
    # Save the result to the output file
    output_filepath = f"resume/resume_delete_experience_not_relate.json"
    with open(output_filepath, "w", encoding="utf-8") as file_save:
        json.dump(json_file, file_save, ensure_ascii=False, indent=4)
        print(f"Output saved to '{output_filepath}'.")

def resume_improve_experience():
    import json
    # Load the resume data
    file_path = "resume/resume_delete_experience_not_relate.json"

    with open(file_path, "r", encoding="utf-8") as file_load:
        resume_data = json.load(file_load)

    st.write("### Improving Work Experience Achievements")
    work_experience = resume_data.get("work_experience", [])

    if "work_experience" not in st.session_state:
        st.session_state.work_experience = work_experience

    # Process achievements and validate them
    for job in work_experience:
        print(f"\nEvaluating achievements for: {job['job_title']} at {job['company']}\n")
        for i, achievement in enumerate(job["achievement"]):
            while True:
                is_valid, feedback = validate_with_gemini(job['job_title'], achievement)
                if is_valid:
                    print(f"✅ Valid achievement: {achievement}")
                    break
                else:
                    print(f"\n❌ Needs improvement: {achievement}")
                    print(f"Suggested improvement: {feedback}")
                    achievement = input("Please rewrite the achievement with improvements: ")
            
            # Save the validated achievement
            job["achievement"][i] = achievement

    # Save the updated JSON file
    output_file = "resume/resume_updated.json"
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(resume_data, file, indent=4, ensure_ascii=False)

    ### Add more skills
    input_filepath = f"resume/resume_missing_skills.json"
    with open(input_filepath, "r", encoding="utf-8") as file_load:
        missing_skills = json.load(file_load)

    # Process missing technical and soft skills
    
    # Extract company names from work experience
    companies = list({exp["key"] for exp in resume_data.get("work_experience", [])})

    # Dictionary to store user responses
    save_answers = {}

    """Prompts the user for missing skills, asks for the company, and validates responses with Gemini."""
    for skill_type, skills in missing_skills.items():  # Iterate over "technical_skills" and "soft_skills"
        for skill in skills:  # Iterate over the skills within each type
            answer = input(f"Do you have experience with {skill}? (yes/no): ").strip().lower()

            if answer == "yes":
                # Display a numbered list of companies
                print("\nSelect the company where you gained experience with this skill:")
                for i, company in enumerate(companies, 1):
                    print(f"{i}. {company}")

                while True:
                    try:
                        company_index = int(input("Enter the number corresponding to the company: ").strip())
                        if 1 <= company_index <= len(companies):
                            selected_company = companies[company_index - 1]
                            break
                        else:
                            print("Invalid selection. Please enter a valid number from the list.")
                    except ValueError:
                        print("Invalid input. Please enter a number.")

                while True:
                    detail = input(f"Describe your experience with {skill}, including how you obtained it and a metric or result achieved: ")

                    is_valid, feedback = validate_with_gemini(skill, detail)

                    if is_valid:
                        if selected_company not in save_answers:
                            save_answers[selected_company] = {"technical_skills": {}, "soft_skills": {}}
                        save_answers[selected_company][skill_type][skill] = detail  # Use skill_type for classification
                        print("Response accepted.")
                        break
                    else:
                        print("Your answer needs improvement.")
                        print(f"Example: {feedback}")
                        print("Please try again with more detail.")

    # Save user responses to a JSON file
    with open("resume/resume_user_answers.json", "w") as file:
        json.dump(save_answers, file, indent=4)

    # Join user answers with resume update
    
    input_filepath = "resume/resume_updated.json"
    with open(input_filepath, "r", encoding="utf-8") as file_load:
        resume_update = json.load(file_load)

    input_filepath = "resume/resume_user_answers.json"
    with open(input_filepath, "r", encoding="utf-8") as file_load:
        user_answers = json.load(file_load)
    
    # Check if user_answers is empty
    if not user_answers:
        with open("resume/resume_final_experience.json", "w") as file:
            json.dump(resume_update, file, indent=4)
    else:
        # Iterate over work experiences in resume_update
        for experience in resume_update["work_experience"]:
            job_key = experience["key"]  # Get the key of the work experience

            if job_key in user_answers:  # Check if there is additional information in user_answers
                new_achievements = []

                # Add technical skills achievements
                for skill, detail in user_answers[job_key].get("technical_skills", {}).items():
                    new_achievements.append(f"Technical Skill - {skill}: {detail}")

                # Add soft skills achievements
                for skill, detail in user_answers[job_key].get("soft_skills", {}).items():
                    new_achievements.append(f"Soft Skill - {skill}: {detail}")

                # Extend existing achievements with the new ones
                experience["achievement"].extend(new_achievements)
        
        with open("resume/resume_final_experience.json", "w") as file:
            json.dump(resume_update, file, indent=4)

    # Display updated result
    import json
    print(json.dumps(resume_update, indent=4))

import re
model_gemini = "models/gemini-2.0-flash"
def validate_with_gemini(skill, detail):
    validation_prompt = (
        f"Evaluate the following response regarding experience with {skill}. "
        f"Ensure it includes:\n"
        f"- A clear explanation of how the experience was obtained.\n"
        f"- At least one action verb describing what was done.\n"
        f"- At least one quantifiable metric or measurable impact, which can be either:\n"
        f"  - A percentage improvement (e.g., 'Increased efficiency by 25%').\n"
        f"  - A numerical value (e.g., 'Led a team of 10 engineers').\n\n"
        f"Response to evaluate:\n{detail}\n\n"
        f"### Evaluation Criteria ###\n"
        f"- If the response meets all criteria, return: 'Evaluation: ✅ Strong response.'\n"
        f"- If the response is missing details, return: 'Evaluation: ❌ Needs improvement.' "
        f"and provide a rewritten version of the response following a strong format.\n\n"
        f"### Example of a strong response ###\n"
        f"'Implemented a predictive maintenance system using Python, reducing machine downtime by 25% over six months.'\n"
        f"'Led a team of 10 engineers in developing an AI-driven analytics tool, improving operational efficiency by 20%.'\n\n"
        f"Now, if the response needs improvement, provide a corrected version formatted as:\n"
        f"'Example: [Your improved response here]'"
    )
    
    genai.configure(api_key = your_api_key)
    model = genai.GenerativeModel(
    model_gemini,
    system_instruction=validation_prompt,
    )

    try:
        response = model.generate_content(validation_prompt)
        feedback = response.text.strip()

        if "✅ Strong response" in feedback:
            return True, feedback
        elif "❌ Needs improvement" in feedback:
            improved_response_match = re.search(r"Example:\s*(.+)", feedback, re.IGNORECASE)
            if improved_response_match:
                example = improved_response_match.group(1).strip()
            else:
                example = "Ensure you include a percentage or numerical value, such as 'Reduced processing time by 30%' or 'Led a team of 5 engineers'."
            return False, example
    except Exception as e:
        print(f"Error communicating with Gemini: {e}")
        return False, "Ensure you include a percentage or numerical value."