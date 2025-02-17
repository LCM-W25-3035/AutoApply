# option1.py
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
    uploaded_cv = st.file_uploader("Upload your PDF resume", type=["pdf"])
    job_selection_method = st.radio("How would you like to provide the job details?", ["Option 1: Upload a job description", "Option 2: Select from our job database"])
    
    if job_selection_method == "Option 1: Upload a job description":
        uploaded_job = st.file_uploader("Upload your PDF Job Description", type=["pdf"])

    else:
        jobs = pd.DataFrame(list(collection.find({}, {"_id": 0, "Title": 1, "Location": 1})))
        selected_job = st.selectbox("Choose a job from our database:", jobs["Title"]) 
        uploaded_job = collection.find_one({"Title": selected_job})
    
    if ((uploaded_cv is not None) and (uploaded_job is not None)):
        
        extract_cv_information(uploaded_cv)
        extract_job_posting_information(uploaded_job)
        customize_resume(uploaded_cv)
        # st.download_button("Download Tailored Resume", customized_cv, file_name="Tailored_Resume.pdf")