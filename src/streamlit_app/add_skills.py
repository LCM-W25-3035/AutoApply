import json
import streamlit as st
import pandas as pd
import google.generativeai as genai
from io import BytesIO
import numpy as np
import re
from utils import validate_with_gemini
import time

var_back_to_job_seleccion = "⬅️ Back to Job Selection"

def run():
    st.markdown("<h1 style='text-align: center; font-size: 50px;'>Add Skills For My Resume</h1>", unsafe_allow_html=True)

    # Check if there are skills to process
    st.session_state.count_key_area = st.session_state.count_key_area + 1

    if(len(st.session_state.skills_add_achievements) > 0):
        
        add_skill = st.session_state.skills_add_achievements[0]

        st.write(f"**Skill to add achievements:** {add_skill}")

        choice = st.selectbox(f"Do you have experience with {add_skill}?", ("yes", "no"))

        if choice == "no":
            st.session_state.skills_add_achievements.pop(0)  # Eliminar la primera habilidad si selecciona "no"
            st.warning(f"Removed skill: {add_skill}")
            st.rerun()
        else:
            st.success(f"Proceeding with skill: {add_skill}")

            # Example list of companies (you can replace this with dynamic data)
            jobs_keys = st.session_state.jobs_keys

            # Let user select the company where they gained experience with this skill
            selected_key = st.selectbox("Select the Company - Job Name where you gained experience:", jobs_keys)

            st.write(f"**Hint to add achievements:** {st.session_state.to_improve_feedback}")
            # Let user describe their experience with this skill
            achievement_description = st.text_input(
                "Describe your experience with this skill, including how you obtained it and a metric or result achieved:",
                key = add_skill
            )
            if achievement_description:
                # Load the resume data
                file_path = "resume/resume_delete_experience_not_relate.json"

                with open(file_path, "r", encoding="utf-8") as file_load:
                    job_experience = json.load(file_load)

                selected_job = next((job for job in job_experience["work_experience"] if job["key"] == selected_key), None)

                is_valid, feedback = validate_with_gemini(selected_job['job_title'], achievement_description)
                st.session_state.to_improve_feedback = feedback
                if is_valid:
                    st.session_state.skill_pass.append(
                            {
                            "job_key": selected_job['key'],
                            "skill": add_skill,
                            "achievement": achievement_description
                        }
                    )
                    st.session_state.skills_add_achievements.pop(0)
                    st.success("✅ Achievement improved and validated successfully!")
                    st.session_state.to_improve_feedback = "No feedback"
                    time.sleep(1)
                    st.rerun()
                else:
                     st.error("⚠️ The achievement description needs improvement. Please try again.")
                     st.write(f"**Hint to add achievements:** {feedback}")

    if(len(st.session_state.skills_add_achievements) == 0):

        output_file = "resume/resume_user_answers.json"
        with open(output_file, "w", encoding="utf-8") as file:
            json.dump(st.session_state.skill_pass, file, indent=4, ensure_ascii=False)

        st.session_state.page = "customization_cv"
        st.rerun()
