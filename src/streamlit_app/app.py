import openai
import json
import streamlit as st
import pandas as pd
import google.generativeai as genai
from pypdf import PdfReader
from io import BytesIO
import pymongo
import numpy as np
# from sentence_transformers import SentenceTransformer
# from sklearn.metrics.pairwise import cosine_similarity


@st.cache_data
def load_jobs_data():
    return pd.read_csv("jobs/jobs_dataset.csv")  # Adjust the file path

# Load the data once
df_jobs = load_jobs_data()

# Application Title
st.title("IT Job Filter in Canada")

# Upload a PDF file
uploaded_pdf = st.file_uploader("Upload a PDF file", type="pdf")

if uploaded_pdf is not None:
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


    genai.configure(api_key="")
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


# Show all jobs by default
st.write(f"Total jobs: {len(df_jobs)}")
st.dataframe(df_jobs)

# Enable filters if the user selects the option
if st.sidebar.checkbox("Do you want to apply filters?"):
    # Input filters
    st.sidebar.header("Search Filters")

    # Cities or Provinces of Canada
    locations = sorted(df_jobs["Location"].dropna().unique().tolist())
    selected_location = st.sidebar.multiselect("Select cities", locations)

    # Main IT Roles
    top_roles = sorted(df_jobs["Job Title"].dropna().unique().tolist())
    selected_roles = st.sidebar.multiselect("Select IT roles", top_roles)

    # Experience Levels
    experience_levels = sorted(df_jobs["Experience Level"].dropna().unique().tolist())
    selected_levels = st.sidebar.multiselect("Select experience levels", experience_levels)

    # Apply filters if any selection exists
    filtered_jobs = df_jobs[
        (df_jobs["Location"].isin(selected_location) if selected_location else True) &
        (df_jobs["Job Title"].isin(selected_roles) if selected_roles else True) &
        (df_jobs["Experience Level"].isin(selected_levels) if selected_levels else True)
    ]

    # Show the filtered results
    st.write(f"Filtered results: {len(filtered_jobs)} jobs found")
    st.dataframe(filtered_jobs)


# MONGO_URI="mongodb+srv://DavidRocha:davidoscar@capstone.9ajag.mongodb.net/?retryWrites=true&w=majority&appName=Capstone"
# MONGO_DB_NAME="jobsDB"
# MONGO_JOBS_COLLECTION="jobsCollection"

# if not MONGO_URI or not MONGO_DB_NAME or not MONGO_JOBS_COLLECTION:
#     print("Error: Missing MongoDB credentials in the .env file.")
#     exit()

# # MongoDB Connection
# client_mongo = pymongo.MongoClient(MONGO_URI)
# db = client_mongo[MONGO_DB_NAME]
# collection = db[MONGO_JOBS_COLLECTION]

# print("Las colecciones disponibles son:", db.list_collection_names())

# Read the jobs.csv file (load it from the backend or a fixed location)
