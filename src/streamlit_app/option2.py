import streamlit as st
import pandas as pd
import pymongo

def run():
    st.markdown("""
        <h1 style='text-align: center; font-size: 50px;'>Find the Best Job Matches</h1>
        <p style='text-align: center; font-size: 20px;'>Use the filters to narrow down job postings and let our AI recommend the best options.</p>
    """, unsafe_allow_html=True)

    # MongoDB Connection
    MONGO_URI = "mongodb+srv://DavidRocha:davidoscar@capstone.9ajag.mongodb.net/?retryWrites=true&w=majority&appName=Capstone"
    MONGO_DB_NAME = "jobsDB"
    MONGO_JOBS_COLLECTION = "jobsCollection"

    client_mongo = pymongo.MongoClient(MONGO_URI)
    db = client_mongo[MONGO_DB_NAME]
    collection = db[MONGO_JOBS_COLLECTION]

    # Load jobs from MongoDB
    jobs_data = list(collection.find({}))  # Retrieve all job postings

    if not jobs_data:
        st.error("❌ No job postings found in the database.")
        return
    
    for job in jobs_data:
        job["_id"] = str(job["_id"])  # Convert ObjectId to string

    # Convert to DataFrame
    df = pd.DataFrame(jobs_data)
    df.rename(columns={"_id": "Job ID", "Title": "Job Title", "Location": "City", "job_category_app": "Category"}, inplace=True)

    # Ensure "Category" is a list
    df["Category"] = df["Category"].apply(lambda x: x if isinstance(x, list) else [])

    # Sidebar Filters
    st.sidebar.header("🔍 Filter Jobs")
    
    category_options = ["All", "Software Development", "Data Science & Machine Learning", "Data Engineering",
                        "Cloud & DevOps", "Cybersecurity", "Business Intelligence & Data Analytics",
                        "IT Support & SysAdmin", "Product Management & Agile Roles", "AI Research & NLP",
                        "Blockchain & Web3", "Embedded Systems & IoT", "Game Development",
                        "Networking & Telecommunications", "Quality Assurance (QA) & Testing",
                        "IT Sales & Pre-Sales"]
    
    city_options = ["All"] + sorted(df["City"].dropna().unique().tolist())
    
    selected_city = st.sidebar.selectbox("🌍 Select a City", city_options)
    selected_category = st.sidebar.selectbox("📌 Select a Category", category_options)

    # Apply Filters
    filtered_df = df.copy()

    if selected_city != "All":
        filtered_df = filtered_df[filtered_df["City"] == selected_city]

    if selected_category != "All":
        filtered_df = filtered_df[filtered_df["Category"].apply(lambda x: selected_category in x)]

    # Job Count
    total_jobs = len(filtered_df)
    if total_jobs == 0:
        st.warning("⚠️ No jobs found matching your filters.")
        return

    # Pagination
    rows_per_page = 20
    total_pages = (total_jobs // rows_per_page) + (1 if total_jobs % rows_per_page > 0 else 0)
    page_number = st.sidebar.slider("📄 Page", 1, total_pages, 1) if total_pages > 1 else 1

    start_idx = (page_number - 1) * rows_per_page
    end_idx = min(start_idx + rows_per_page, total_jobs)

    st.write(f"📌 Showing {start_idx + 1} - {end_idx} of {total_jobs} jobs")

    # Display Paginated DataFrame
    st.dataframe(filtered_df.iloc[start_idx:end_idx])

    # Run AI Job Recommender
    if st.button("🤖 Find Best Job Matches with AI Recommender"):
        st.session_state['filtered_jobs'] = filtered_df
        st.session_state.page = "option2_1"
        st.rerun()

    # Back to Home
    if st.button("⬅️ Back to Home"):
        st.session_state.page = "Home"
        st.rerun()
