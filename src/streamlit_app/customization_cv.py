import json
import streamlit as st
import pandas as pd
import google.generativeai as genai
from io import BytesIO
import numpy as np
import re
from utils import join_all_resume_json, generate_cv
import os



var_back_to_job_seleccion = "⬅️ Back to Job Selection"

def run():
    st.markdown("<h1 style='text-align: center; font-size: 50px;'>Customization CV - Download CV</h1>", unsafe_allow_html=True)
    
    input_filepath = "resume/resume_updated.json"
    with open(input_filepath, "r", encoding="utf-8") as file_load:
        resume_update = json.load(file_load)

    input_filepath = "resume/resume_user_answers.json"
    if os.path.exists(input_filepath):
        with open(input_filepath, "r", encoding="utf-8") as file_load:
            user_answers_list = json.load(file_load)
    else:
        user_answers_list = []

    user_answers = {}
    for entry in user_answers_list:
        job_key = entry["job_key"]
        achievement = entry["achievement"]
        
        if job_key not in user_answers:
            user_answers[job_key] = [] 
        
        user_answers[job_key].append(achievement) 

    if not user_answers:
        output_filepath = "resume/resume_final_experience.json"
        with open(output_filepath, "w", encoding="utf-8") as file:
            json.dump(resume_update, file, indent=4)
    else:

        for experience in resume_update["work_experience"]:
            job_key = experience["key"]

            if job_key in user_answers: 
                if "achievement" not in experience:
                    experience["achievement"] = []

                for achievement in user_answers[job_key]:
                    if achievement not in experience["achievement"]:
                        experience["achievement"].append(achievement)

        with open("resume/resume_final_experience.json", "w", encoding="utf-8") as file:
            json.dump(resume_update, file, indent=4)

    join_all_resume_json()
    generate_cv()

    json_file_path = f"resume/resume_final_to_word.json"
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    user_name = data.get('personal_information', {}).get('name', 'Unknown').strip()
    user_name = " ".join(user_name.title().split())
    output_path = f"output/{user_name}_customization.docx" 

    # Read the file in binary mode
    with open(output_path, "rb") as file:
        file_bytes = file.read()

    # Download button
    if st.download_button(
        label="📥 Download personalized CV",
        data=file_bytes,
        file_name="customization_cv.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ):
        st.session_state.page = "Home"
        if "app_initialized" in st.session_state:
            del st.session_state.app_initialized
        st.rerun()
        
    # Download the word file
    if st.button("🏠 Back to Home"):
        st.session_state.page = "Home"
        if "app_initialized" in st.session_state:
            del st.session_state.app_initialized
        st.rerun()