import streamlit as st
from utils import extract_cv_information, extract_job_posting_information_from_str
import pymongo
import pandas as pd
from bson import ObjectId  # Required for handling MongoDB ObjectId
var_back_to_job_seleccion = "⬅️ Back to Job Selection"
print("entro option 2_2")
def run():
    st.markdown("<h1 style='text-align: center; font-size: 50px;'>Tailor My Resume for the Selected Jobs</h1>", unsafe_allow_html=True)

    selected_job = st.session_state["selected_jobs"]

    for index, row in selected_job.iterrows():
        extract_job_posting_information_from_str(row["Job Description"], index)

    uploaded_cv = st.session_state["uploaded_cv"]

    # Process when both CV and job data are available
    if uploaded_cv is not None:
        st.write("Processing your resume...")

        extract_cv_information(uploaded_cv)

        st.write("Your resume for this application should be:")
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
