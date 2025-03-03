# option1.py
import pymongo
from pypdf import PdfReader
import docx
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import streamlit as st
import google.generativeai as genai
import io
from io import BytesIO
from utils import extract_cv_information, extract_job_posting_information

def run():

    st.markdown("<h1 style='text-align: center; font-size: 50px;'>Find the best job matches</h1>", unsafe_allow_html=True)
    
    st.write("Here you can upload your resume and find the best job matches.")

    uploaded_cv = st.file_uploader("Upload your PDF resume", type=["pdf"])
    job_filter_selection = st.radio("Do you like to filter your job search?", ["Option 1: YES", "Option 2: NO"], index=None)
    
    if job_filter_selection == "Option 1: YES":
        uploaded_job = st.file_uploader("Upload your PDF Job Description", type=["pdf"])
        if not MONGO_URI or not MONGO_DB_NAME or not MONGO_JOBS_COLLECTION:
            print("Error: Missing MongoDB credentials.")
            exit()

    if job_filter_selection == "Option 2: NO":
        jobs = pd.DataFrame(list(collection.find({}, {"_id": 0, "Title": 1, "Location": 1})))
        selected_job = st.selectbox("Choose a job from our database:", jobs["Title"]) 
        uploaded_job = collection.find_one({"Title": selected_job})
    
    if ((uploaded_cv is not None) and (uploaded_job is not None)):
        
        extract_cv_information(uploaded_cv)
        extract_job_posting_information(uploaded_job)
        customize_resume(uploaded_cv)
        # st.download_button("Download Tailored Resume", customized_cv, file_name="Tailored_Resume.pdf")

        # Button to go back
    if st.button("⬅️ Back to Home"):
        st.session_state.page = "Home"
        st.rerun()