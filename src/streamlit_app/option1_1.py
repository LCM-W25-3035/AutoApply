# option1.py
import streamlit as st
from utils import extract_cv_information, extract_job_posting_information,resume_education_info_personal,resume_promt_summary,resume_delete_experience_not_related,resume_skills, validate_with_gemini
import json

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
        resume_education_info_personal()
        resume_promt_summary()
        resume_skills()
        resume_delete_experience_not_related()

        # Check if all achievements are empty
        # Load the resume data
        file_path = "resume/resume_delete_experience_not_relate.json"
        with open(file_path, "r", encoding="utf-8") as file_load:
            filter_to_continue = json.load(file_load)

        if all(not experience["achievement"] for experience in filter_to_continue["work_experience"]):
            print("entro line 46")
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
            st.session_state.page == "analize_skills"
            
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

            # Show results
            st.write("## ✅ Validated Achievements")
            st.write(st.session_state.achievements_pass)

            st.write("## ❌ Achievements that need improvement")
            for item in st.session_state.achievements_do_not_pass:
                st.write(f"- **{item['key']}**: {item['achievement']}")

            st.session_state.page = "improve_skills"
            if st.button("Improve skills"):
                st.write(st.session_state.page)
                st.rerun()