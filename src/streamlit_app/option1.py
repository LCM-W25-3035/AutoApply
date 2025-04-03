import streamlit as st

def go_to_page(page_name):
    st.session_state.page = page_name
    st.rerun()

def run():
    st.markdown("<h1 style='text-align: center; font-size: 50px;'>Tailor my resume for a specific job opportunity</h1>", unsafe_allow_html=True)
    
    job_selection_method = st.radio("How would you like to provide the job details?", [
        "Option 1: Upload a job description",
        "Option 2: Select from our job database"
    ], index=None, key="paso_1")

    if job_selection_method == "Option 1: Upload a job description":
        go_to_page("Option1_1")

    if job_selection_method == "Option 2: Select from our job database":
        go_to_page("Option1_2")

    if st.button("⬅️ Back to Home"):
        if "app_initialized" in st.session_state:
            del st.session_state.app_initialized
        go_to_page("Home")
