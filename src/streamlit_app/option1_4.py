import streamlit as st
from utils import extract_cv_information, extract_job_posting_information_from_str, resume_education_info_personal,resume_promt_summary,resume_delete_experience_not_related,resume_skills, validate_with_gemini,ats_score_evaluation_pre,export_match_and_missing_skills
import pymongo
import pandas as pd
from bson import ObjectId  # Required for handling MongoDB ObjectId
import json
import time

var_back_to_job_seleccion = "⬅️ Back to Job Selection"

def run():
    st.markdown("<h1 style='text-align: center; font-size: 50px;'>Tailor My Resume for the Selected Job</h1>", unsafe_allow_html=True)

    # Ensure a job was selected in the previous step
    if "selected_job_id" not in st.session_state or st.session_state.selected_job_id is None:
        st.error("⚠️ No job selected. Please go back and select a job first.")
        if st.button(var_back_to_job_seleccion):
            st.session_state.page = "Option1_2"
            st.rerun()
        return

    # MongoDB Connection
    MONGO_URI = st.secrets["api_keys"]["MONGODB_URI"]
    MONGO_DB_NAME = st.secrets["api_keys"]["MONGODB_NAME"]
    MONGO_JOBS_COLLECTION = st.secrets["api_keys"]["MONGODB_JOBS_COLLECTION"]

    client_mongo = pymongo.MongoClient(MONGO_URI)
    db = client_mongo[MONGO_DB_NAME]
    collection = db[MONGO_JOBS_COLLECTION]

    # Retrieve selected job details
    job_id = ObjectId(st.session_state.selected_job_id)  # Convert back to MongoDB ObjectId
    selected_job = collection.find_one({"_id": job_id})
    selected_job["_id"] = str(selected_job["_id"])  # Convert ObjectId to string
    # Ensure the job description field exists
    job_description = selected_job.get("Job Description", "No description available")

    if not selected_job:
        st.error("⚠️ Selected job not found in the database. Please go back and choose another job.")
        if st.button(var_back_to_job_seleccion):
            st.session_state.page = "Option1_2"
            st.rerun()
        return

    # Display job details
    st.subheader("📄 Selected Job")
    job_details = pd.DataFrame([selected_job]).drop(columns=["_id"], errors="ignore")

    st.dataframe(job_details)

    # Upload CV
    st.subheader("📤 Upload Your Resume")
    uploaded_cv = st.file_uploader("Please upload your PDF Resume", type=["pdf"])

    # Process when both CV and job data are available
    if uploaded_cv is not None:
        st.write("Processing your resume and the selected job description...")

        extract_cv_information(uploaded_cv)
        extract_job_posting_information_from_str(job_description)
        ats_score_evaluation_pre()
        export_match_and_missing_skills()
        resume_education_info_personal()
        resume_delete_experience_not_related()
        
        # Check if all achievements are empty
        # Load the resume data
        file_path = "resume/resume_delete_experience_not_relate.json"
        with open(file_path, "r", encoding="utf-8") as file_load:
            filter_to_continue = json.load(file_load)

        if all(not experience["achievement"] for experience in filter_to_continue["work_experience"]):
            st.warning(
                "⚠️ Sorry, none of your experiences match the job posting. "
                "We recommend rewriting your achievements to better highlight relevant skills and trying again. "
                "Click below to return to the home page."
            )
            if st.button("🏠 Back to Home"):
                st.session_state.page = "Home"
                if "app_initialized" in st.session_state:
                    del st.session_state.app_initialized
                st.rerun()
        
        else:
            
            # Initialize session state if it doesn't exist
            if "achievements_pass" not in st.session_state:
                st.session_state.achievements_pass = []

            if "achievements_do_not_pass" not in st.session_state:
                st.session_state.achievements_do_not_pass = []

            # Load the resume data
            file_path = "resume/resume_delete_experience_not_relate.json"

            with open(file_path, "r", encoding="utf-8") as file_load:
                resume_data = json.load(file_load)

            work_experience = resume_data.get("work_experience", [])

            # Process achievements and validate them
            for job in work_experience:
                st.write(f"### Evaluating achievements for: {job['job_title']} in {job['company']}")
                
                for achievement in job["achievement"]:
                    is_valid, feedback = validate_with_gemini(job['job_title'], achievement)

                    if is_valid:
                        st.session_state.achievements_pass.append(
                            {"job_title": job['job_title'], "achievement": achievement, "company":job['company'], "key":job['key'] }
                        )
                    else:
                        st.session_state.achievements_do_not_pass.append(
                            {"job_title": job['job_title'], "achievement": achievement, "feedback": feedback,  "company":job['company'], "key":job['key']}
                        )
                    time.sleep(0.2)

            st.session_state.page = "information_to_user"
            if st.button("View Compatibility Analysis"):
                st.write(st.session_state.page)
                st.rerun()
