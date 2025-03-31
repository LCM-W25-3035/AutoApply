import streamlit as st
import pandas as pd
from utils import extract_cv_information, key_words_match_jobs_resume, extract_keywords_with_gemini

def run():
    st.markdown("""
        <h1 style='text-align: center; font-size: 50px;'>Upload Your Resume</h1>
        <p style='text-align: center; font-size: 20px;'>We will match your resume with the best job postings based on similarity.</p>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader("📂 Upload your resume (TXT or PDF)", type=["txt", "pdf"])

    if uploaded_file is not None and "top_matches" not in st.session_state:
        extract_cv_information(uploaded_file)
        key_words_candidate = extract_keywords_with_gemini()
        filtered_df = st.session_state['filtered_jobs']
        if filtered_df.shape[0] > 1500:
            filtered_df_str = filtered_df.iloc[:1500][['Job ID', 'key_words_app']].to_string(index=False)
        else:
            filtered_df_str = filtered_df[['Job ID', 'key_words_app']].to_string(index=False)

        top_matches2 = key_words_match_jobs_resume(key_words_candidate, filtered_df_str)
        top_matches2 = pd.DataFrame(top_matches2)

        filtered_df = filtered_df[filtered_df['Job ID'].isin(top_matches2['Job ID'])]
        filtered_df = filtered_df.merge(top_matches2, on='Job ID')
        top_matches = filtered_df.sort_values(by="similarity", ascending=False).head(10)

        st.session_state.top_matches = top_matches

    if "top_matches" in st.session_state:
        top_matches = st.session_state.top_matches
        st.dataframe(top_matches.drop(columns=["key_word_app", "key_words_app"]))

        job_id_input = st.text_input("Enter the Job ID to proceed:", key="job_id_input")

        if job_id_input:
            if job_id_input in top_matches["Job ID"].astype(str).values:
                st.success(f"✅ Job ID {job_id_input} selected! Proceeding to the next step...")
                st.session_state["selected_jobs"] = top_matches.loc[top_matches["Job ID"] == job_id_input]
                st.session_state.page = "Option2_2"
                st.rerun()
            else:
                st.error("⚠️ Invalid Job ID. Please enter a valid ID from the table.")

    if st.button("⬅️ Back to Job Selection"):
        st.session_state.page = "Option2"
        st.rerun()
