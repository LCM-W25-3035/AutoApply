import streamlit as st
from utils import extract_cv_information, extract_job_posting_information_from_str, customize_cv, generate_cv
import pymongo
import pandas as pd
from bson import ObjectId  # Required for handling MongoDB ObjectId
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
    MONGO_URI = "mongodb+srv://DavidRocha:davidoscar@capstone.9ajag.mongodb.net/?retryWrites=true&w=majority&appName=Capstone"
    MONGO_DB_NAME = "jobsDB"
    MONGO_JOBS_COLLECTION = "jobsCollection"

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
        st.write("✅ Your resume has been tailored for this job application!")

    # Navigation buttons
    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button(var_back_to_job_seleccion):
            st.session_state.page = "Option1_2"
            st.rerun()

    with col2:
        if st.button("🏠 Back to Home"):
            st.session_state.page = "Home"
            st.rerun()
