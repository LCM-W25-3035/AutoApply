import streamlit as st
import json
import pandas as pd
import google.generativeai as genai
from pypdf import PdfReader
from io import BytesIO
import numpy as np
import re
from utils import validate_with_gemini
import time

var_back_to_job_seleccion = "⬅️ Back to Job Selection"

def run():
    st.markdown("<h1 style='text-align: center; font-size: 50px;'>Results of your Resume</h1>", unsafe_allow_html=True)

    with open("resume/ats_score_evaluation_pre.json", "r", encoding="utf-8") as file:
        ats = json.load(file)

    st.write(f"**Your ATS Score is:** {ats['ats_score']}")
    
    st.write(f"**Your ATS Recommendations:**")
    for item in ats['recommendations']:
        st.write(f" - {item}")

    st.markdown("<h1 style='text-align: center; font-size: 40px;'>Competences</h1>", unsafe_allow_html=True)

    st.write(f"✅ We've identified relevant skills on your resume for this job")

    for item in ats["matching_technical_skills"]:
        st.write(f"-    {item}")

    for item in ats["matching_soft_skills"]:
        st.write(f"-    {item}")

    st.write(f"✅ We've identified relevant achivement on your resume for this job")
    for item in st.session_state.achievements_pass:
        st.write(f"- **{item['key']}**: {item['achievement']}")

    st.markdown("<h1 style='text-align: center; font-size: 40px;'>Competences to Improve</h1>", unsafe_allow_html=True)


    st.write(f"❌ We've identified relevant achivement on your resume for this job that you can make them stand out even more by using action-oriented language and including specific evidence or measurable outcomes.")
    for item in st.session_state.achievements_do_not_pass:
        st.write(f"- **{item['key']}**: {item['achievement']}")

    st.write(f"Missing But Relevant Skills! ❌ We found additional skills that are important for this job posting, but we didn't see them in your resume. These skills could strengthen your application and increase your chances of passing ATS filters..")

    for item in ats["missing_technical_skills"]:
        st.write(f"-    {item}")

    for item in ats["missing_soft_skills"]:
        st.write(f"-    {item}")

    # Navigation buttons
    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("Improve CV"):
            st.session_state.page = "improve_skills"
            st.rerun()

    with col2:
        if st.button("🏠 Back to Home"):
            st.session_state.page = "Home"
            if "app_initialized" in st.session_state:
                del st.session_state.app_initialized
            st.rerun()