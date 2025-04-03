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
    st.markdown("<h1 style='text-align: center; font-size: 50px;'>Improve Skills For My Resume</h1>", unsafe_allow_html=True)
    
    if "achievement" not in st.session_state:
        st.session_state.achievement = "Inicialice Achivement"

    if "count_key_area" not in st.session_state:
        st.session_state.count_key_area = 0

    if (len(st.session_state.achievements_do_not_pass) > 0):
        to_improve = st.session_state.achievements_do_not_pass[0]
        print(to_improve)
        st.write(f"**Current Achievement:** {to_improve['achievement']}")
        st.write(f"**Hint to Improve achievement:** {to_improve['feedback']}")
        # improved_achievement = st.text_input("Please rewrite the achievement with improvements:", value=to_improve["feedback"])
        improved_achievement = st.text_input(
            "Please describe your achievement, including how you obtained it and a metric or result achieved",
            key = to_improve['achievement']
        )
        print(improved_achievement)

        if improved_achievement:
            is_valid, feedback = validate_with_gemini(to_improve['job_title'], improved_achievement)
            if is_valid:
                st.session_state.achievements_pass.append(
                    {"job_title": to_improve['job_title'], "achievement": improved_achievement, "company":to_improve['company'], "key":to_improve['key'] }
                )
                st.session_state.achievements_do_not_pass.pop(0)
                st.success("✅ Achievement improved and validated successfully!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("⚠️ The achievement description needs improvement. Please try again.")
                st.write(f"**Hint to add achievements:** {feedback}")

    else:
        output_file = "resume/resume_updated.json"
        with open(output_file, "w", encoding="utf-8") as file:
            json.dump(st.session_state.achievements_pass, file, indent=4, ensure_ascii=False)

        # Load the data from the original file with the complete structure
        with open("resume/resume_delete_experience_not_relate.json", "r", encoding="utf-8") as file:
            resume_data = json.load(file)

        # Load the data with the updated achievements
        with open("resume/resume_updated.json", "r", encoding="utf-8") as file:
            updated_achievements = json.load(file)

        # Create a dictionary to quickly access achievements by key
        achievements_dict = {}
        for item in updated_achievements:
            key = item["key"]
            if key in achievements_dict:
                achievements_dict[key].append(item["achievement"])
            else:
                achievements_dict[key] = [item["achievement"]]

        # Create a dictionary to quickly access achievements by key
        for experience in resume_data["work_experience"]:
            key = experience["key"]
            if key in achievements_dict:
                experience["achievement"] = achievements_dict[key]

        with open("resume/resume_updated.json", "w", encoding="utf-8") as file:
            json.dump(resume_data, file, indent=4, ensure_ascii=False)

        ### add more skills
        input_filepath = f"resume/resume_missing_skills.json"
        with open(input_filepath, "r", encoding="utf-8") as file_load:
            missing_skills = json.load(file_load)
        missing_skills = sum(missing_skills.values(), [])


        ### add more skills
        file_path = "resume/resume_delete_experience_not_relate.json"
        with open(file_path, "r", encoding="utf-8") as file_load:
            resume_data = json.load(file_load)

        # Process missing technical and soft skills
        
        # Extract company names from work experience
        jobs_keys = list({exp["key"] for exp in resume_data.get("work_experience", [])})

        # Initialize the session state if it does not exist
        if "jobs_keys" not in st.session_state:
            st.session_state.jobs_keys = jobs_keys
            print(st.session_state.jobs_keys)

        if "skills_add_achivments" not in st.session_state:
            st.session_state.skills_add_achievements = missing_skills
            print(st.session_state.skills_add_achievements)

        st.session_state.page = "add_skills"
        st.session_state.skill_pass = []
        st.session_state.to_improve_feedback = "No feedback"
        st.rerun()

