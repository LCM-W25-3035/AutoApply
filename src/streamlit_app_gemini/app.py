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
    You are an HR analyst and you receive resumes and you must analyze it to answer:
    A. Identify and list all ***technical skills*** (e.g., programming languages, frameworks, libraries, databases, cloud platforms, and tools) explicitly mentioned in the resume.
    B. Identify and list all ***soft skills*** (e.g., leadership, teamwork, adaptability, problem-solving, communication, critical thinking, emotional intelligence) found in the resume that also you can infer from the resume.
    C. How many years of total professional experience does the candidate have?
    D. Identify and list all education levels obtained by the candidate, along with the corresponding fields of study.
    E. What is the candidate's highest level of experience based on job roles, industries, and responsibilities?
    F. Identify and list all the ***key achievements*** of the candidate, along with relevant context. Ensure each achievement includes:
       - The **problem or challenge** addressed.
       - The **technologies or methodologies** used.
       - The **impact or measurable outcome** (e.g., improved efficiency by 80%, reduced costs by 30%).
    G. What are the candidate's areas of domain expertise (e.g., Machine Learning, Cloud Computing, Data Science, Cybersecurity)?
    H. What job titles has the candidate held in previous roles?
    I. In which industries has the candidate worked?
    J. Find the professional summary.

    Return only the JSON response in the exact structure below, without any explanations or extra text:

    {{
      "technical_skills": [A],
      "soft_skills": [B],
      "years_of_experience": C,
      "education": [
       {{
       "level": "D",
       "field": "D"}}
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

    genai.configure(api_key="")
    model = genai.GenerativeModel(
    "models/gemini-2.0-flash",
    system_instruction=system_instructions,
    )

    response = model.generate_content(f"The resume to analyze is {pdf_text}")
    cleaned_response = response.text.strip("```json\n").strip("```").replace("\n", "")

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


MONGO_URI="mongodb+srv://DavidRocha:davidoscar@capstone.9ajag.mongodb.net/?retryWrites=true&w=majority&appName=Capstone"
MONGO_DB_NAME="jobsDB"
MONGO_JOBS_COLLECTION="jobsCollection"

if not MONGO_URI or not MONGO_DB_NAME or not MONGO_JOBS_COLLECTION:
    print("Error: Missing MongoDB credentials in the .env file.")
    exit()

# MongoDB Connection
client_mongo = pymongo.MongoClient(MONGO_URI)
db = client_mongo[MONGO_DB_NAME]
collection = db[MONGO_JOBS_COLLECTION]

print("Las colecciones disponibles son:", db.list_collection_names())

# Read the jobs.csv file (load it from the backend or a fixed location)
