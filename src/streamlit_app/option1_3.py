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
import pymongo

def run():
    st.markdown("<h1 style='text-align: center; font-size: 50px;'>Tailor my resume for a specific job opportunity</h1>", unsafe_allow_html=True)
    st.write("Here you can upload your resume and customize it for a job opportunity.")
    
    st.write("")
    
    uploaded_cv = None
    uploaded_cv = st.file_uploader("Please upload your PDF Resume", type=["pdf"])

    st.write("")

    uploaded_job = None
    uploaded_job = st.file_uploader("Please upload your PDF Job Description", type=["pdf"])

    if ((uploaded_cv is not None) and (uploaded_job is not None)):
        extract_cv_information(uploaded_cv)
        extract_job_posting_information(uploaded_job)
        st.write("Your resume for this application should be:")

    if st.button("⬅️ Back to Home"):
        st.session_state.page = "Home"
        st.rerun()