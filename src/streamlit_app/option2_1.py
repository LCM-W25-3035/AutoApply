import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from pypdf import PdfReader

def run():
    st.markdown("""
        <h1 style='text-align: center; font-size: 50px;'>Upload Your Resume</h1>
        <p style='text-align: center; font-size: 20px;'>We will match your resume with the best job postings based on similarity.</p>
    """, unsafe_allow_html=True)

    # Upload Resume
    uploaded_file = st.file_uploader("📂 Upload your resume (TXT or PDF)", type=["txt", "pdf"])
    
    if uploaded_file is not None:
        # Read file
        file_extension = uploaded_file.name.split(".")[-1]
        
        if file_extension == "txt":
            resume_text = uploaded_file.getvalue().decode("utf-8")
        elif file_extension == "pdf":
            reader = PdfReader(uploaded_file)
            resume_text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
        else:
            st.error("Unsupported file format. Please upload a .txt or .pdf file.")
            return
        
        st.session_state["uploaded_cv_pdf"] = uploaded_file
        st.session_state["uploaded_cv_str"] = resume_text
        
        # Extract job descriptions
        filtered_df = st.session_state['filtered_jobs']
        job_descriptions = filtered_df["Job Description"].astype(str).tolist()
        
        # Compute TF-IDF vectors
        vectorizer = TfidfVectorizer(stop_words='english')
        job_vectors = vectorizer.fit_transform(job_descriptions)
        resume_vector = vectorizer.transform([resume_text])
        
        # Compute cosine similarity
        similarities = cosine_similarity(resume_vector, job_vectors)[0]
        filtered_df["similarity"] = similarities
        
        # Get top 10 most relevant jobs
        top_matches = filtered_df.sort_values(by="similarity", ascending=False).head(10)
        
        st.write("### 🏆 Top 10 Job Matches for You")
        
        if "selected_jobs" not in st.session_state:
            st.session_state["selected_jobs"] = []
        
        # Display top job matches with selection buttons
        for index, row in top_matches.iterrows():
            col1, col2 = st.columns([5, 1])
            with col1:
                st.dataframe(pd.DataFrame(row).transpose())  # Show single-row DataFrame
            with col2:
                if st.button(f"Select {index}", key=f"select_{index}"):
                    st.session_state["selected_jobs"].append(row.to_dict())

        st.write("### Job Selected By You")
        st.dataframe(pd.DataFrame(st.session_state["selected_jobs"]))
        
        # Proceed button
        if st.button("➡️ Proceed with Selected Jobs"):
            if not st.session_state["selected_jobs"]:
                st.warning("⚠️ Please select at least one job to continue.")
            else:
                st.session_state["selected_jobs"] = pd.DataFrame(st.session_state["selected_jobs"])
                st.session_state.page = "Option2_2"
                st.rerun()
    
    # Back to Job Selection
    if st.button("⬅️ Back to Job Selection"):
        st.session_state.page = "Option2"
        st.rerun()
