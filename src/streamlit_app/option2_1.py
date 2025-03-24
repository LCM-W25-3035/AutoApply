import streamlit as st
import pandas as pd
from utils import extract_key_words_from_cv, extract_cv_information, jaccard_similarity

def normalize_keyword_list(keyword_list):
    if not isinstance(keyword_list, list):
        return set()
    return set(tuple(sorted(word_list)) for word_list in keyword_list if isinstance(word_list, list))

def run():
    st.markdown("""
        <h1 style='text-align: center; font-size: 50px;'>Upload Your Resume</h1>
        <p style='text-align: center; font-size: 20px;'>We will match your resume with the best job postings based on similarity.</p>
    """, unsafe_allow_html=True)

    # Upload Resume
    uploaded_file = st.file_uploader("📂 Upload your resume (TXT or PDF)", type=["txt", "pdf"])
    
    if uploaded_file is not None:
        # Read file
        extract_cv_information(uploaded_file)
        keyword_set = extract_key_words_from_cv()

        # Extract job descriptions
        filtered_df = st.session_state['filtered_jobs']

        # Aplicar la transformación
        filtered_df["key_word_app_normalized"] = filtered_df["key_word_app"].apply(normalize_keyword_list)

        filtered_df["similarity"] = filtered_df["key_word_app_normalized"].apply(lambda job_kw: jaccard_similarity(keyword_set, job_kw))
        
        # Get top 10 most relevant jobs based on Jaccard similarity
        top_matches = filtered_df.sort_values(by="similarity", ascending=False).head(10)

        # Display paginated DataFrame
        st.dataframe(top_matches)

        # Job Selection
        job_id_input = st.text_input("Enter the Job ID to proceed:", key="job_id_input")

        if job_id_input:
            if job_id_input in top_matches["Job ID"].astype(str).values:
                st.success(f"✅ Job ID {job_id_input} selected! Proceeding to the next step...")
                st.session_state["selected_jobs"] = top_matches.loc[top_matches["Job ID"]==job_id_input]
                st.session_state.page = "Option2_2"
                st.rerun()
            else:
                st.error("⚠️ Invalid Job ID. Please enter a valid ID from the table.")
    
    # Back to Job Selection
    if st.button("⬅️ Back to Job Selection"):
        st.session_state.page = "Option2"
        st.rerun()
