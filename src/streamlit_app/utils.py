import openai
import json
import streamlit as st
import pandas as pd
import google.generativeai as genai
from pypdf import PdfReader
from io import BytesIO
import numpy as np
import re

your_api_key = ""
model_gemini = "models/gemini-2.0-flash"
clean_json = "```json\n"


def resume_improve_experience2():
    file_path = "resume/resume_delete_experience_not_relate.json"

    # Load data only once
    if "resume_data" not in st.session_state:
        with open(file_path, "r", encoding="utf-8") as file_load:
            st.session_state.resume_data = json.load(file_load)
        st.session_state.current_job = 0
        st.session_state.current_achievement = 0
        st.session_state.answers = {}

    resume_data = st.session_state.resume_data
    work_experience = resume_data.get("work_experience", [])

    if not work_experience:
        st.error("No work experience found.")
        return

    job_index = st.session_state.current_job
    achievement_index = st.session_state.current_achievement

    if job_index >= len(work_experience):
        st.success("All achievements have been reviewed!")
        return

    job = work_experience[job_index]
    achievements = job.get("achievement", [])

    if achievement_index >= len(achievements):
        st.session_state.current_job += 1
        st.session_state.current_achievement = 0
        st.rerun()

    achievement = achievements[achievement_index]
    key = f"{job['job_title']}_{achievement_index}"

    is_valid, feedback = validate_with_gemini(job['job_title'], achievement)

    st.chat_message("assistant").write(f"**Evaluating:** {achievement}")

    if is_valid:
        st.chat_message("assistant").write("✅ This achievement is strong.")
    else:
        st.chat_message("assistant").write(f"❌ Needs improvement: {feedback}")

    user_input = st.chat_input("Rewrite the achievement:")

    if user_input:
        st.session_state.answers[key] = user_input
        st.session_state.current_achievement += 1
        st.rerun()

    if st.session_state.current_job >= len(work_experience):
        st.success("Resume improvements completed!")
        save_improved_resume(resume_data, st.session_state.answers)

def save_improved_resume(resume_data, answers):
    """Save the improvements in the JSON file"""
    for job in resume_data["work_experience"]:
        for i, achievement in enumerate(job["achievement"]):
            key = f"{job['job_title']}_{i}"
            if key in answers:
                job["achievement"][i] = answers[key]

    with open("resume/resume_updated.json", "w", encoding="utf-8") as file:
        json.dump(resume_data, file, indent=4, ensure_ascii=False)

    st.success("Resume experience improvements saved successfully!")



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

    ### add more skills
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
                # Show numbered list of companies
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
                        save_answers[selected_company][skill_type][skill] = detail  # Use skill_type to classify
                        print("Response accepted.")
                        break
                    else:
                        print("Your answer needs improvement.")
                        print(f"Example: {feedback}")
                        print("Please try again with more detail.")

    
    # Save user responses to a JSON file
    with open("resume/resume_user_answers.json", "w") as file:
        json.dump(save_answers, file, indent=4)

    # Join user_answer with resume_update
    
    input_filepath = "resume/resume_updated.json"
    with open(input_filepath, "r", encoding="utf-8") as file_load:
        resume_update = json.load(file_load)

    input_filepath = "resume/resume_user_answers.json"
    with open(input_filepath, "r", encoding="utf-8") as file_load:
        user_answers = json.load(file_load)
    # Check if `user_answers` is empty
    if not user_answers:
        with open("resume/resume_final_experience.json", "w") as file:
            json.dump(resume_update, file, indent=4)
    else:

        # Iterate over work experiences in resume_update
        for experience in resume_update["work_experience"]:
            job_key = experience["key"]  # Get the work experience key

            if job_key in user_answers:  # Check if there is additional information in user_answers
                new_achievements = []

                # Add technical skill achievements
                for skill, detail in user_answers[job_key].get("technical_skills", {}).items():
                    new_achievements.append(f"Technical Skill - {skill}: {detail}")

                # Add soft skill achievements
                for skill, detail in user_answers[job_key].get("soft_skills", {}).items():
                    new_achievements.append(f"Soft Skill - {skill}: {detail}")

                # Extend existing achievements with new ones
                experience["achievement"].extend(new_achievements)
        
        with open("resume/resume_final_experience.json", "w") as file:
            json.dump(resume_update, file, indent=4)

    # View updated result
    import json
    print(json.dumps(resume_update, indent=4))
def join_all_resume_json():
    input_filepath = "resume/resume_education_info_personal.json"
    with open(input_filepath, "r", encoding="utf-8") as file_load:
       education_personal = json.load(file_load)

    input_filepath = "resume/resume_summary.json"
    with open(input_filepath, "r", encoding="utf-8") as file_load:
       summary = json.load(file_load)

    input_filepath = "resume/resume_user_answers.json"
    with open(input_filepath, "r", encoding="utf-8") as file_load:
       user_answers = json.load(file_load)

    input_filepath = "resume/resume_match_skills.json"
    with open(input_filepath, "r", encoding="utf-8") as file_load:
       skills_json = json.load(file_load)

    # Create a set to avoid duplicates
    combined_skills = set(skills_json["technical_skills"] + skills_json["soft_skills"])

    # Add skills from user_answers
    for key, skills in user_answers.items():
        combined_skills.update(skills.get("technical_skills", {}).keys())
        combined_skills.update(skills.get("soft_skills", {}).keys())

    # Convert the set to a list and structure it in the new JSON
    final_skills_json = {"skills": list(combined_skills)}

    input_filepath = "resume/resume_final_experience.json"
    with open(input_filepath, "r", encoding="utf-8") as file_load:
       final_experience = json.load(file_load)

    final_resume_json = {
        "education": education_personal.get("education", []),
        "personal_information": education_personal.get("personal_information", []),
        "professional_summary": summary.get("professional_summary", []),
        "skills": final_skills_json.get("skills", []),
        "work_experience": final_experience.get("work_experience",[])
    }

    # Save the updated JSON file
    output_file = "resume/resume_final_to_word.json"
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(final_resume_json , file, indent=4, ensure_ascii=False)

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
def resume_skills():
    # Specify the path of the file to be read
    input_filepath = f"resume/resume.json"

    with open(input_filepath, "r", encoding="utf-8") as file_load:
       cv_data = json.load(file_load)

    # Specify the path of the file to be read
    input_filepath = f"resume/job_posting.json"

    with open(input_filepath, "r", encoding="utf-8") as file_load:
       job_data = json.load(file_load)

    # Extract skills from resume and job posting
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

    # Create a JSON file with matched skills
    match_skills = {
        "technical_skills": match_technical_skills,
        "soft_skills": match_soft_skills
    }

    # Save missing skills to a JSON file
    with open("resume/resume_missing_skills.json", "w") as file:
        json.dump(missing_skills, file, indent=4)
    print("Skills missing saved in 'resume/resume_missing_skills.json'.")

    # Save matched skills to a JSON file
    with open("resume/resume_match_skills.json", "w") as file:
        json.dump(match_skills, file, indent=4)
    print("Skills matched saved in 'resume/resume_match_skills.json'.")


def resume_education_info_personal():
    # Specify the path of the file to be read
    input_filepath = f"resume/resume.json"

    with open(input_filepath, "r", encoding="utf-8") as file_load:
       original_cv = json.load(file_load)
    
    output_file = {
        "personal_information": original_cv.get("personal_information", {}),
        "education": original_cv.get("education", {})
    }

    # Save the result to the output file
    output_filepath = f"resume/resume_education_info_personal.json"
    with open(output_filepath, "w", encoding="utf-8") as file_save:
        json.dump(output_file, file_save, ensure_ascii=False, indent=4)
        print(f"Output saved to '{output_filepath}'.")


def resume_promt_summary():
    # Specify the path of the file to be read
    input_filepath = f"resume/resume.json"

    with open(input_filepath, "r", encoding="utf-8") as file_load:
       resume = json.load(file_load)
    
    # Specify the path of the file to be read
    input_filepath = f"resume/job_posting.json"

    with open(input_filepath, "r", encoding="utf-8") as file_load:
       job_offer = json.load(file_load)
    

    system_instructions ="""
    You are an HR specialist skilled in processing and analyzing resumes.
    Your task is to generate a concise and professional summary strictly based on the provided resume.

    **Instructions:**
    - Use only the information available in the resume. Do not infer or add any details that are not explicitly mentioned.
    - Focus on highlighting relevant experience, skills, and qualifications.
    - Ensure clarity, coherence, and alignment with the job offer.
    - The response must be in JSON format only, without any explanations or additional text.

    **Output Format:**
    {
        "professional_summary": "Generated summary here"
    }
    """

    genai.configure(api_key = your_api_key)
    model = genai.GenerativeModel(
    model_gemini,
    system_instruction=system_instructions,
    )

    response = model.generate_content(f"The resume to analyze is {resume} and the job offer is {job_offer}")
    cleaned_response = response.text.strip(clean_json).strip("```").replace("\n", "")

    json_file = json.loads(cleaned_response)
    print("The real json line 209", json_file)

    # Save the result to the output file
    output_filepath = f"resume/resume_summary.json"
    with open(output_filepath, "w", encoding="utf-8") as file_save:
        json.dump(json_file, file_save, ensure_ascii=False, indent=4)
        print(f"Output saved to '{output_filepath}'.")
def resume_delete_experience_not_related():
    # Specify the path of the file to be read
    input_filepath = f"resume/resume.json"

    with open(input_filepath, "r", encoding="utf-8") as file_load:
       resume = json.load(file_load)
    
    job_experience = {"work_experience": resume.get("work_experience", {})}
    
    # Specify the path of the file to be read
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

    response = model.generate_content(f"The work experience section to analyze is {job_experience} and the job offer is {job_offer}")
    cleaned_response = response.text.strip(clean_json).strip("```").replace("\n", "")
    print(cleaned_response)
    json_file = json.loads(cleaned_response)
    # Save the result to the output file
    output_filepath = f"resume/resume_delete_experience_not_relate.json"
    with open(output_filepath, "w", encoding="utf-8") as file_save:
        json.dump(json_file, file_save, ensure_ascii=False, indent=4)
        print(f"Output saved to '{output_filepath}'.")


def customize_cv() -> dict:
    """
    Customizes the CV based on the extracted CV data and the job offer data.
    Both inputs are dictionaries parsed from JSON.
    
    The output JSON should include all important personal details (Name, Email, Phone, SocialMedia)
    along with a structured breakdown:
      - "Summary": <Rewritten summary text>,
      - "Skills": <Rewritten skills text>,
      - "Experience": [ { "Company": <Company name>, "Dates": <Start date - End date>, "Functions": <Rewritten description> }, ... ],
      - "Education": [ { "Institution": <Institution name>, "Dates": <Start date - End date>, "Degree": <Degree obtained> }, ... ]
      
    Do not invent new content; only enhance and reorganize the existing information.
    """

    # Specify the path of the file to be read
    input_filepath = f"resume/resume.json"

    # Open and load the content of the JSON file
    with open(input_filepath, "r", encoding="utf-8") as file_load:
        original_cv = json.load(file_load)

    # Specify the path of the file to be read
    input_filepath = f"resume/job_posting.json"

    # Open and load the content of the JSON file
    with open(input_filepath, "r", encoding="utf-8") as file_load:
        job_description = json.load(file_load)\
    
    prompt = f"""
    Using the following inputs, generate a revised version of the CV that improves the wording and structure to clearly emphasize the candidate's relevant skills and experiences for the job offer.
    Do not invent any new content; only enhance and reorganize the existing information.

    Original CV:
    {original_cv}

    Job Offer:
    {job_description}

    Please output the rewritten CV in a structured JSON format with the following keys:

    {{
    "PersonalInfo": {{
        "Name": "<Candidate's full name>",
        "Address": "<Candidate's location Address>",
        "Email": "<Candidate's email address>",
        "Phone": "<Candidate's phone number>",
        "SocialMedia": "<Links to social media profiles or other contact details>"
    }},
    "Summary": "<Rewritten summary text>",
    "Skills": "<Rewritten skills text>",
    "Experience": [
        {{
        "Company": "<Company name>",
        "Dates": "<Start date - End date>",
        "Functions": "<Rewritten description of responsibilities and functions>"
        }}
    ],
    "Education": [
        {{
        "Institution": "<Institution name>",
        "Dates": "<End date>",
        "Degree": "<Degree obtained>"
        }}
    ]
    }}

    Ensure the JSON is valid.
    """
    genai.configure(api_key = your_api_key)
    model = genai.GenerativeModel(
    model_gemini
    )
    response = model.generate_content(prompt)

    cleaned_response = response.text.strip(clean_json).strip("```").replace("\n", "")

    json_file = json.loads(cleaned_response)
    # Save the result to the output file
    output_filepath = f"resume/resume_customization.json"
    with open(output_filepath, "w", encoding="utf-8") as file_save:
        json.dump(json_file, file_save, ensure_ascii=False, indent=4)
        print(f"Output saved to '{output_filepath}'.")
import json
import logging
from io import BytesIO
from pypdf import PdfReader
import google.generativeai as genai

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def extract_cv_information(uploaded_pdf):
    """Extracts key details from a resume PDF and saves them in a JSON file."""
    
    try:
        # Read the PDF content using PyPDF
        pdf_reader = PdfReader(BytesIO(uploaded_pdf.getvalue()))
        pdf_text = ""
        
        for page in pdf_reader.pages:
            text = page.extract_text()
            if text:
                pdf_text += text + "\n"
        
        if not pdf_text.strip():
            logging.warning("No text found in the provided PDF.")
            return

        system_instructions = """
        You are an HR analyst responsible for processing and analyzing resumes. Your task is to extract the following information from a given resume:

        1. Technical Skills:
            - Identify and list all technical skills explicitly mentioned in the resume.
            - These may include programming languages, frameworks, libraries, databases, cloud platforms, and relevant tools.
        2. Soft Skills:
            - Identify and list all soft skills mentioned in the resume.
            - Additionally, infer soft skills based on the candidate's experience, achievements, and responsibilities.
            - Examples include leadership, teamwork, adaptability, problem-solving, communication, critical thinking, and emotional intelligence.
        3. Years of Experience:
            - Calculate and provide the total number of years of professional experience.
        4. Education:
            - Extract and list all education details, including:
                - Degree
                - Institution
                - Location
                - Start date
                - End date
        5. Experience Level:
            - Determine the candidate's highest level of experience based on job roles, industries, and responsibilities.
        6. Work Experience:
            - Extract all previous job positions and structure them as a list of dictionaries, where each dictionary represents a job.
            - Each dictionary must contain:
                - Job title
                - Company
                - Location
                - Start date
                - End date
                - Achievements and responsibilities associated with that role
        7. Professional Summary:
            - Extract the professional summary from the resume.
        8. Languages & Proficiency (Optional: If not found, omit this section):
            - Identify all languages spoken by the candidate and their proficiency level.
            - If no language information is found, exclude this section from the final JSON.
        9. Certifications (Optional: If not found, omit this section):
            - List all certifications the candidate has obtained, including:
                - Certification name
                - Issuing organization
                - Year issued
                - If no certifications are found, exclude this section from the final JSON.
        10. Personal Information:
            - Name
            - Phone
            - Email
            - Address
            - Identify and list Social media links

        11. Output Format:
            - Return only the JSON response in the exact structure below.
            - Do not include any explanations, extra text, or formatting beyond the JSON itself.

            {
            "technical_skills": [A],
            "soft_skills": [B],
            "years_of_experience": C,
            "education": [
                {
                "degree": D,
                "institution": D,
                "location": D,
                "start_date": D, 
                "end_date": D 
                }
            ],
            "experience_level": E,
            "work_experience": [
                {
                "job_title": F,
                "company": F,
                "location": F,
                "start_date": F,
                "end_date": F,
                "key": "company-job_title",
                "achievement": [F]
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
                "year_issued": I
                }
            ],
            "personal_information":{
                "name": J,
                "phone": J,
                "email": J,
                "address": J,
                "social_media": [J]
            }
            }
        """

        genai.configure(api_key=your_api_key)
        model = genai.GenerativeModel(
            model_gemini,
            system_instruction=system_instructions,
        )

        response = model.generate_content(f"The resume to analyze is: {pdf_text}")
        cleaned_response = response.text.strip(clean_json).strip("```").replace("\n", "")

        # Convert response to JSON
        json_file = json.loads(cleaned_response)

        # Save the result to the output file
        output_filepath = "resume/resume.json"
        with open(output_filepath, "w", encoding="utf-8") as file_save:
            json.dump(json_file, file_save, ensure_ascii=False, indent=4)

        logging.info(f"Output saved to '{output_filepath}'.")
    
    except Exception as e:
        logging.error(f"Error processing resume: {e}")

import json
import logging
from io import BytesIO
from pypdf import PdfReader
import google.generativeai as genai

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def extract_job_posting_information(uploaded_job):
    """Extracts structured information from a job posting PDF and saves it as JSON."""
    
    try:
        # Read the PDF content using PyPDF
        pdf_reader = PdfReader(BytesIO(uploaded_job.getvalue()))
        pdf_text = ""

        for page in pdf_reader.pages:
            text = page.extract_text()
            if text:
                pdf_text += text + "\n"
        
        if not pdf_text.strip():
            logging.warning("No text found in the provided job posting PDF.")
            return

        system_instructions = """
        You are a job market analyst specializing in processing and analyzing job postings. 
        Your task is to extract key information from a given job listing and structure it into a JSON format. 
        The extracted data should include:

        1. Job Information:
            - The job title of the position.
        2. Company Information:
            - The company name offering the position.
            - The industry in which the company operates.
            - The location where the job is based.
            - Whether the job is remote-friendly (true/false).
        3. Employment Type & Experience Level:
            - The employment type (e.g., Full-time, Part-time, Contract, Internship).
            - The experience level required (e.g., Junior, Mid, Senior, Lead).
            - The minimum years of experience required.
        4. Salary Information:
            - The salary range (minimum and maximum salary).
            - The currency in which the salary is offered.
            - The payment frequency (e.g., Hourly, Monthly, Annual).
        5. Job Description:
            - A short summary of the job description provided in the job posting.
        6. Responsibilities:
            - A list of job responsibilities as mentioned in the posting.
        7. Requirements:
            - A list of all mandatory job requirements specified in the posting.
        8. Skills Required:
            - Identify and list all technical skills required for the job.
            - Identify and list all soft skills required or implied in the posting.
        9. Education & Certifications (Optional: If not found, omit these sections):
            - Identify the minimum education level required (degree and field of study).
            - List any preferred institutions mentioned in the job description.
            - Identify any required certifications, including the certification name and issuing organization.
        10. Language Requirements (Optional: If not found, omit this section):
            - Identify all languages required for the job, along with the proficiency level.
        11. Benefits & Perks (Optional: If not found, omit this section):
            - Extract and list all benefits mentioned in the job posting (e.g., health insurance, remote work, bonuses, flexible hours).
        12. Application Information:
            - The application deadline (if provided).
            - The job posting date (if available).
            - The official application link where candidates can apply.

        13. Output Format:
            - Return ONLY the JSON response in the exact structure below.
            - Do NOT include any explanations, comments, or extra text beyond the JSON itself.

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

        genai.configure(api_key=your_api_key)
        model = genai.GenerativeModel(
            model_gemini,
            system_instruction=system_instructions,
        )

        response = model.generate_content(f"The job posting to analyze is: {pdf_text}")
        cleaned_response = response.text.strip(clean_json).strip("```").replace("\n", "")

        # Convert response to JSON
        json_file = json.loads(cleaned_response)

        # Save the result to the output file
        output_filepath = "resume/job_posting.json"
        with open(output_filepath, "w", encoding="utf-8") as file_save:
            json.dump(json_file, file_save, ensure_ascii=False, indent=4)

        logging.info(f"Output saved to '{output_filepath}'.")

    except Exception as e:
        logging.error(f"Error processing job posting: {e}")


import json
import logging
import google.generativeai as genai

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def extract_job_posting_information_from_str(uploaded_job):
    """Extracts structured information from a job posting string and saves it as JSON."""
    
    try:
        # Ensure the input is not empty
        pdf_text = uploaded_job.strip()
        if not pdf_text:
            logging.warning("No text found in the job posting string.")
            return

        system_instructions = """
        You are a job market analyst specializing in processing and analyzing job postings. 
        Your task is to extract key information from a given job listing and structure it into a JSON format. 
        The extracted data should include:

        1. Job Information:
            - The job title of the position.
        2. Company Information:
            - The company name offering the position.
            - The industry in which the company operates.
            - The location where the job is based.
            - Whether the job is remote-friendly (true/false).
        3. Employment Type & Experience Level:
            - The employment type (e.g., Full-time, Part-time, Contract, Internship).
            - The experience level required (e.g., Junior, Mid, Senior, Lead).
            - The minimum years of experience required.
        4. Salary Information:
            - The salary range (minimum and maximum salary).
            - The currency in which the salary is offered.
            - The payment frequency (e.g., Hourly, Monthly, Annual).
        5. Job Description:
            - A short summary of the job description provided in the job posting.
        6. Responsibilities:
            - A list of job responsibilities as mentioned in the posting.
        7. Requirements:
            - A list of all mandatory job requirements specified in the posting.
        8. Skills Required:
            - Identify and list all technical skills required for the job.
            - Identify and list all soft skills required or implied in the posting.
        9. Education & Certifications (Optional: If not found, omit these sections):
            - Identify the minimum education level required (degree and field of study).
            - List any preferred institutions mentioned in the job description.
            - Identify any required certifications, including the certification name and issuing organization.
        10. Language Requirements (Optional: If not found, omit this section):
            - Identify all languages required for the job, along with the proficiency level.
        11. Benefits & Perks (Optional: If not found, omit this section):
            - Extract and list all benefits mentioned in the job posting (e.g., health insurance, remote work, bonuses, flexible hours).
        12. Application Information:
            - The application deadline (if provided).
            - The job posting date (if available).
            - The official application link where candidates can apply.

        13. Output Format:
            - Return ONLY the JSON response in the exact structure below.
            - Do NOT include any explanations, comments, or extra text beyond the JSON itself.

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

        genai.configure(api_key=your_api_key)
        model = genai.GenerativeModel(
            model_gemini,
            system_instruction=system_instructions,
        )

        response = model.generate_content(f"The job posting to analyze is: {pdf_text}")
        cleaned_response = response.text.strip(clean_json).strip("```").replace("\n", "")

        # Convert response to JSON
        json_file = json.loads(cleaned_response)

        # Save the result to the output file
        output_filepath = "resume/job_posting.json"
        with open(output_filepath, "w", encoding="utf-8") as file_save:
            json.dump(json_file, file_save, ensure_ascii=False, indent=4)

        logging.info(f"Output saved to '{output_filepath}'.")

    except json.JSONDecodeError:
        logging.error("Failed to parse the JSON response from the AI model.")
    except Exception as e:
        logging.error(f"Error processing job posting: {e}")
import json
import re
import logging
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import google.generativeai as genai

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def find_best_jobs(cv_file, job_offers):
    """Finds the top 10 best matching jobs using cosine similarity."""
    try:
        # Extract text from the resume file
        cv_text = extract_text_from_file(cv_file)

        # Extract job descriptions and titles
        job_texts = [job.get("Description", "") for job in job_offers]
        job_titles = [job.get("Title", "Unknown Job") for job in job_offers]

        # Ensure there are job postings to compare
        if not job_texts:
            logging.warning("No job postings found.")
            return pd.DataFrame()

        # Compute TF-IDF vectors
        vectorizer = TfidfVectorizer(stop_words="english")
        tfidf_matrix = vectorizer.fit_transform([cv_text] + job_texts)

        # Calculate cosine similarity
        similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

        # Get indices of top 10 matches
        best_matches_idx = similarities.argsort()[-10:][::-1]

        # Store best job matches
        best_jobs = [{"Title": job_titles[i], "Similarity": round(similarities[i], 4)} for i in best_matches_idx]

        return pd.DataFrame(best_jobs)

    except Exception as e:
        logging.error(f"Error in find_best_jobs: {e}")
        return pd.DataFrame()

def skills_missing():
    """Identifies missing skills and prompts the user for details."""

    try:
        # Load resume data
        with open("resume/resume.json", "r", encoding="utf-8") as file:
            cv_data = json.load(file)

        # Load job posting data
        with open("resume/job_posting.json", "r", encoding="utf-8") as file:
            job_data = json.load(file)

        # Extract technical skills from both sources
        cv_skills = set(cv_data.get("technical_skills", []))
        job_skills = set(job_data.get("technical_skills", []))

        # Identify missing skills (limit to 5)
        missing_skills = list(job_skills - cv_skills)[:5]

        if not missing_skills:
            logging.info("No missing skills identified.")
            return

        # Dictionary to store user responses
        save_answers = {}

        for skill in missing_skills:
            user_input = input(f"Do you have experience with {skill}? (yes/no): ").strip().lower()

            if user_input == "yes":
                while True:
                    # Ask the user to describe their experience
                    detail = input(f"Describe your experience with {skill}, including how you obtained it and a measurable result: ")

                    # Validate the response with Gemini AI
                    validation_prompt = (
                        f"Evaluate the following response regarding experience with {skill}. "
                        f"Ensure it includes:\n"
                        f"- A clear explanation of how the experience was obtained.\n"
                        f"- At least one action verb describing what was done.\n"
                        f"- A quantifiable metric or measurable impact.\n\n"
                        f"Response to evaluate:\n{detail}\n\n"
                        f"### Evaluation Criteria ###\n"
                        f"- If the response meets all criteria, return: '✅ Strong response.'\n"
                        f"- If the response is missing details, return: '❌ Needs improvement.' "
                        f"and provide an improved example.\n\n"
                        f"### Example of a strong response ###\n"
                        f"'Implemented a predictive maintenance system using Python, reducing machine downtime by 25% over six months.'\n"
                    )

                    try:
                        genai.configure(api_key=your_api_key)
                        model = genai.GenerativeModel(model_gemini, system_instruction=validation_prompt)
                        response = model.generate_content(validation_prompt)
                        feedback = response.text.strip()

                        # Check if response is strong
                        if re.search(r"✅ Strong response", feedback, re.IGNORECASE):
                            save_answers[skill] = detail
                            break  # Exit loop when answer is valid

                        # Provide an improvement example if needed
                        if re.search(r"❌ Needs improvement", feedback, re.IGNORECASE):
                            print("\n⚠️ Your answer needs improvement.")
                            example_match = re.search(r"Example of a strong response:\s*(.+)", feedback, re.IGNORECASE)

                            if example_match:
                                print(f"\n🔄 Example of how you should structure your answer:\n{example_match.group(1).strip()}")

                            print("\nPlease try again with more details using action verbs and metrics.")

                    except Exception as e:
                        logging.error(f"Error communicating with Gemini: {e}")
                        print("Skipping this skill...")
                        break  # Move to the next skill

        # Save responses to a JSON file
        with open("resume/user_answers.json", "w", encoding="utf-8") as file:
            json.dump(save_answers, file, indent=4, ensure_ascii=False)

        logging.info("✅ Answers saved successfully.")

    except Exception as e:
        logging.error(f"Error in skills_missing: {e}")
   


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

# Reference
# (OpenAI, ChatGPT o1, first prompt, 2025): I have this template in Word, this Json, both have the same keys, guide me to make a code that reeplace the information in the template with the info in Json
# (Claude, 3.5 Sonnet, last prompt, 2025): The template is not filling completly good, help me to correct the format

import re
import json
import os
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
# from docx2pdf import convert

def split_into_sentences(text):
    print("split_into_sentences line", 839)
    """Splits the text into sentences using punctuation."""
    print(text)
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    print(sentences)
    output = [s.strip() for s in sentences if s.strip()]
    print("split_into_sentences line", 844)
    return output
    

class CVGenerator:
    CUSTOM_BULLET_STYLE = 'Custom Bullet'
    
    def _init_(self, template_path):
        self.doc = Document(template_path)
        self.setup_styles()
        
    def setup_styles(self):
        print("setup_styles line", 852)
        """Set up document styles."""
        styles = self.doc.styles
        
        # Normal style
        style = styles['Normal']
        style.font.name = 'Calibri'
        style.font.size = Pt(11)
        style.paragraph_format.space_after = Pt(0)
        style.paragraph_format.space_before = Pt(0)
        
        # Custom bullet style
        if self.CUSTOM_BULLET_STYLE not in styles:
            bullet_style = styles.add_style(self.CUSTOM_BULLET_STYLE, WD_STYLE_TYPE.PARAGRAPH)
            bullet_style.base_style = styles['Normal']
            bullet_style.paragraph_format.left_indent = Inches(0.25)
            bullet_style.paragraph_format.first_line_indent = Inches(-0.25)
            
    def add_bullet_paragraph(self, text):
        print("add_bullet_paragraph line", 871)
        """Add a bullet point paragraph."""
        paragraph = self.doc.add_paragraph()
        paragraph.style = self.CUSTOM_BULLET_STYLE
        paragraph.paragraph_format.left_indent = Inches(0.25)
        paragraph.paragraph_format.first_line_indent = Inches(-0.25)
        run_bullet = paragraph.add_run('• ')
        run_bullet.bold = True
        paragraph.add_run(text.strip())
        return paragraph
        
    def add_section_title(self, title):
        print("add_section_title line", 883)
        """Add a section title with proper formatting."""
        # Add space before section
        spacing_para = self.doc.add_paragraph()
        spacing_para.paragraph_format.space_before = Pt(12)
        
        # Section title
        paragraph = self.doc.add_paragraph()
        paragraph.add_run(title).bold = True
        self.add_horizontal_line(paragraph)
        
    def add_horizontal_line(self, paragraph):
        print("add_horizontal_line line", 895)
        """Add a horizontal line after a section title."""
        p = paragraph._p
        p_pr = p.get_or_add_pPr()
        bottom_border = OxmlElement('w:pBdr')
        bottom = OxmlElement('w:bottom')
        bottom.set(qn('w:val'), 'single')
        bottom.set(qn('w:sz'), '6')
        bottom_border.append(bottom)
        p_pr.append(bottom_border)
        
    def add_right_aligned_text(self, paragraph, text):
        print("add_right_aligned_text line", 907)
        """Add right aligned text to a paragraph using tab stops."""
        paragraph.paragraph_format.tab_stops.clear_all()
        paragraph.paragraph_format.tab_stops.add_tab_stop(
            Inches(8), WD_TAB_ALIGNMENT.RIGHT
        )
        paragraph.add_run('\t' + text)
        
    def fill_cv(self, data):
        print("fill_cv line", 916)
        """Fill the CV with the provided data."""
        # Clear the document
        for paragraph in self.doc.paragraphs[:]:
            p = paragraph._element
            p.getparent().remove(p)
            
        # Name
        print("fill_cv line", 924)
        name_paragraph = self.doc.add_paragraph()
        name_text = data.get('personal_information', {}).get('name', '')
        name_run = name_paragraph.add_run(name_text)
        name_run.bold = True
        name_run.font.size = Pt(48)

        print("fill_cv line", 931)
        # Contact information (including Social Media)
        personal_info = data.get('personal_information', {})
        address = personal_info.get('addres', '')
        phone = personal_info.get('phone', '')
        email = personal_info.get('email', '')
        social_list = personal_info.get('social_media', [])
        social = ", ".join(social_list) if isinstance(social_list, list) else social_list

        print("fill_cv line", 940)
        # Create a contact string that only includes non-empty fields
        contact_parts = [address, phone, email, social]
        contact = " | ".join([str(part) for part in contact_parts if part])
        
        print("fill_cv line", 945)
        contact_paragraph = self.doc.add_paragraph()
        contact_paragraph.add_run(contact)
        contact_paragraph.paragraph_format.space_after = Pt(12)
        
        # Summary (justified)
        print("fill_cv line", 951)
        self.add_section_title("Summary")
        summary_text = data.get('professional_summary', '')
        summary_para = self.doc.add_paragraph()
        summary_para.add_run(summary_text)
        summary_para.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        summary_para.paragraph_format.space_after = Pt(12)
        
        # Experience
        print("fill_cv line", 960)
        self.add_section_title("Experience")
        for exp in data.get('work_experience', []):
            print("fill_cv line 963", exp)
            exp_para = self.doc.add_paragraph()
            exp_para.paragraph_format.space_before = Pt(12)
            job_title = exp.get('job_title', '')
            company = exp.get('company', '')
            location = exp.get('location', '')
            exp_text = f"{job_title} | {company} | {location}"
            exp_run = exp_para.add_run(exp_text)
            exp_run.bold = True
            start_date = exp.get('start_date', '')
            end_date = exp.get('end_date', '')
            dates_text = f"{start_date} - {end_date}"
            self.add_right_aligned_text(exp_para, dates_text)
            
            # Functions (bullet points, justified)
            functions_text = exp.get('achievement', '')
            # functions = split_into_sentences(functions_text)
            functions = functions_text
            for function in functions:
                if function.strip():
                    bullet_para = self.add_bullet_paragraph(function)
                    bullet_para.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                    bullet_para.paragraph_format.space_after = Pt(3)
                    
        # Education
        print("fill_cv line", 986)
        self.add_section_title("Education")
        for edu in data.get('education', []):
            edu_para = self.doc.add_paragraph()
            edu_para.paragraph_format.space_before = Pt(6)
            institution = edu.get('institution', '')
            edu_run = edu_para.add_run(f"{institution}")
            edu_run.bold = True
            dates = edu.get('end_date', '')
            self.add_right_aligned_text(edu_para, dates)
            
            degree_para = self.doc.add_paragraph()
            degree_para.add_run(edu.get('degree', ''))
            degree_para.paragraph_format.space_after = Pt(6)
            
        # Skills in columns
        print("fill_cv line", 1003)
        self.add_section_title("Skills")
        skills_list = data.get('skills', [])  # Obtener la lista directamente
        skills = [skill.strip() for skill in skills_list if isinstance(skill, str)]

        num_columns = 3  # Change to 2 if preferred
        num_skills = len(skills)
        num_rows = (num_skills + num_columns - 1) // num_columns
        
        table = self.doc.add_table(rows=num_rows, cols=num_columns)
        table.autofit = True
        
        print("fill_cv line", 1015)
        skill_index = 0
        for r in range(num_rows):
            row_cells = table.rows[r].cells
            for c in range(num_columns):
                if skill_index < num_skills:
                    paragraph = row_cells[c].paragraphs[0]
                    run = paragraph.add_run('• ' + skills[skill_index])
                    run.font.size = Pt(11)
                    skill_index += 1
                else:
                    row_cells[c].text = ""
    
    def save(self, output_path):
        """Save the document to the specified path."""
        self.doc.save(output_path)
            
def generate_cv():
    json_file_path = f"resume/resume_final_to_word.json"
    template_path = f"template/template1.docx"
    """Generate CV from JSON data"""
    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        print("json_final to word linea 1020",data)
        user_name = data.get('personal_information', {}).get('name', 'Unknown').strip()
        user_name = " ".join(user_name.title().split())
        output_path = f"output/{user_name}_customization.docx"  

       # Create and save the Word version
        generator = CVGenerator(template_path)
        generator.fill_cv(data)
        generator.save(output_path)
        print(f"Word CV generated successfully: {output_path}")
        
        # Convert the Word file to PDF
        # pdf_output = os.path.splitext(output_path)[0] + ".pdf"
        # convert(output_path, pdf_output)
        # print(f"PDF CV generated successfully: {pdf_output}")
        
        return True
        
    except Exception as e:
        print(f"Error generating CV: {str(e)}")
        return False