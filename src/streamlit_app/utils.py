import openai
import json
import streamlit as st
import pandas as pd
import google.generativeai as genai
from pypdf import PdfReader
from io import BytesIO
import numpy as np


your_api_key = ""
model_gemini = "models/gemini-2.0-flash"
clean_json = "```json\n"


def customize_cv(index="") -> dict:
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

    # Especifica la ruta del archivo que deseas leer
    input_filepath = f"resume/resume.json"

    # Abre y carga el contenido del archivo JSON
    with open(input_filepath, "r", encoding="utf-8") as file_load:
        original_cv = json.load(file_load)

    # Especifica la ruta del archivo que deseas leer
    input_filepath = f"resume/job_posting_{index}.json"

    # Abre y carga el contenido del archivo JSON
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
        "Dates": "<Start date - End date>",
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
    output_filepath = f"resume/resume_customization_{index}.json"
    with open(output_filepath, "w", encoding="utf-8") as file_save:
        json.dump(json_file, file_save, ensure_ascii=False, indent=4)
        print(f"Output saved to '{output_filepath}'.")

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

def extract_job_posting_information(uploaded_job,index=""):
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

    output_filepath = f"resume/job_posting_{index}.json"
    with open(output_filepath, "w", encoding="utf-8") as file_save:
        json.dump(json_file, file_save, ensure_ascii=False, indent=4)
        print(f"Output saved to '{output_filepath}'.")



def extract_job_posting_information_from_str(uploaded_job, index=""):

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
    output_filepath = f"resume/job_posting_{index}.json"
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



# Reference
# (OpenAI, ChatGPT o1, first prompt, 2025): I have this template in Word, this Json, both have the same keys, guide me to make a code that reeplace the information in the template with the info in Json
# (Claude, 3.5 Sonnet, last prompt, 2025): The template is not filling completly good, help me to correct the format

from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import json

class CVGenerator:
    CUSTOM_BULLET_STYLE = 'Custom Bullet'
    
    def __init__(self, template_path):
        self.doc = Document(template_path)
        self.setup_styles()
        
    def setup_styles(self):
        """Configure document styles"""
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
        """Add a bullet point paragraph"""
        paragraph = self.doc.add_paragraph()
        paragraph.style = self.CUSTOM_BULLET_STYLE
        paragraph.paragraph_format.left_indent = Inches(0.25)
        paragraph.paragraph_format.first_line_indent = Inches(-0.25)
        paragraph.add_run('• ').bold = True
        paragraph.add_run(text.strip())
        return paragraph
        
    def add_section_title(self, title):
        """Add a section title with proper formatting"""
        # Add space before section
        spacing_para = self.doc.add_paragraph()
        spacing_para.paragraph_format.space_before = Pt(12)
        
        # Add section title
        paragraph = self.doc.add_paragraph()
        paragraph.add_run(title).bold = True
        self.add_horizontal_line(paragraph)
        
    def add_horizontal_line(self, paragraph):
        """Add horizontal line after section titles"""
        p = paragraph._p
        p_pr = p.get_or_add_pPr()
        bottom_border = OxmlElement('w:pBdr')
        bottom = OxmlElement('w:bottom')
        bottom.set(qn('w:val'), 'single')
        bottom.set(qn('w:sz'), '6')
        bottom_border.append(bottom)
        p_pr.append(bottom_border)
        
    def add_right_aligned_text(self, paragraph, text):
        """Add right-aligned text to a paragraph using tab stops"""
        # Clear any existing tab stops
        paragraph.paragraph_format.tab_stops.clear_all()
        
        # Add a right-aligned tab stop at 6 inches
        paragraph.paragraph_format.tab_stops.add_tab_stop(
            Inches(6), WD_TAB_ALIGNMENT.RIGHT
        )
        
        # Add the text with tab
        paragraph.add_run('\t' + text)
        
    def fill_cv(self, data):
        """Fill the CV with the provided data"""
        # Clear the document
        for paragraph in self.doc.paragraphs[:]:
            p = paragraph._element
            p.getparent().remove(p)
            
        # Name
        name_paragraph = self.doc.add_paragraph()
        name_run = name_paragraph.add_run(data['PersonalInfo']['Name'])
        name_run.bold = True
        name_run.font.size = Pt(48)
        
        # Contact Info
        contact = f"{data['PersonalInfo']['Address']} | {data['PersonalInfo']['Phone']} | {data['PersonalInfo']['Email']}"
        contact_paragraph = self.doc.add_paragraph()
        contact_paragraph.add_run(contact)
        contact_paragraph.paragraph_format.space_after = Pt(12)
        
        # Summary
        self.add_section_title("Summary")
        summary_para = self.doc.add_paragraph()
        summary_para.add_run(data['Summary'])
        summary_para.paragraph_format.space_after = Pt(12)
        
        # Experience
        self.add_section_title("Experience")
        for exp in sorted(data['Experience'], key=lambda x: x['Dates'].split('-')[1], reverse=True):
            # Company and dates
            exp_para = self.doc.add_paragraph()
            exp_para.paragraph_format.space_before = Pt(6)
            company_run = exp_para.add_run(f"{exp['Company']}")
            company_run.bold = True
            self.add_right_aligned_text(exp_para, exp['Dates'])
            
            # Functions
            functions = exp['Functions'].split('\n')
            for function in functions:
                if function.strip():
                    bullet_para = self.add_bullet_paragraph(function.strip())
                    bullet_para.paragraph_format.space_after = Pt(3)
        
        # Education
        self.add_section_title("Education")
        for edu in sorted(data['Education'], key=lambda x: x['Dates'].split('-')[1], reverse=True):
            # Institution and dates
            edu_para = self.doc.add_paragraph()
            edu_para.paragraph_format.space_before = Pt(6)
            institution_run = edu_para.add_run(f"{edu['Institution']}")
            institution_run.bold = True
            self.add_right_aligned_text(edu_para, edu['Dates'])
            
            # Degree on next line
            degree_para = self.doc.add_paragraph()
            degree_para.add_run(edu['Degree'])
            degree_para.paragraph_format.space_after = Pt(6)
        
        # Skills
        self.add_section_title("Skills")
        skills = data['Skills'].split(', ')
        for skill in skills:
            bullet_para = self.add_bullet_paragraph(skill.strip())
            bullet_para.paragraph_format.space_after = Pt(3)
    
    def save(self, output_path):
        """Save the document to the specified path"""
        self.doc.save(output_path)

def generate_cv(index=""):
    json_file_path = f"resume/resume_customization_{index}.json"
    template_path = f"template/template1.docx"
    output_path = f"output/cv_customization_{index}.docx" 
    """Generate CV from JSON data"""
    try:
        # Load JSON data
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # Generate CV
        generator = CVGenerator(template_path)
        generator.fill_cv(data)
        generator.save(output_path)
        
        print(f"CV generated successfully: {output_path}")
        return True
        
    except Exception as e:
        print(f"Error generating CV: {str(e)}")
        return False


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
###############################################
def resume_education_info_personal():
    # Specify the path to the file you want to read
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

######################

def resume_promt_summary():
    # Specify the path to the file you want to read
    input_filepath = f"resume/resume.json"

    with open(input_filepath, "r", encoding="utf-8") as file_load:
       resume = json.load(file_load)
    
    # Specify the path to the file you want to read
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
