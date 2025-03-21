import streamlit as st
import pandas as pd
import pymongo

def run():
    st.markdown("<h1 style='text-align: center; font-size: 50px;'>Select a Job from the Database</h1>", unsafe_allow_html=True)

    # MongoDB Connection
    MONGO_URI = st.secrets["api_keys"]["MONGODB_URI"]
    MONGO_DB_NAME = st.secrets["api_keys"]["MONGODB_NAME"]
    MONGO_JOBS_COLLECTION = st.secrets["api_keys"]["MONGODB_JOBS_COLLECTION"]

    client_mongo = pymongo.MongoClient(MONGO_URI)
    db = client_mongo[MONGO_DB_NAME]
    collection = db[MONGO_JOBS_COLLECTION]

    # Load jobs from MongoDB
    jobs_data = list(collection.find({}))  # Retrieve everything

    if not jobs_data:
        st.error("No job postings found in the database.")
        return
    
    for job in jobs_data:
        job["_id"] = str(job["_id"])  # Convert ObjectId to string


    # Convert to DataFrame
    df = pd.DataFrame(jobs_data)
    df = df.rename(columns={"_id": "Job ID", "Title": "Job Title", "Location": "City", "Keyword": "Category"})
 
    # Fill NaN values
    df["Category"] = df["Category"].fillna("Not Determined")
    df["City"] = df["City"].fillna("Unknown")
    
    # Normalize text format
    df["Category"] = df["Category"].str.title()
    df["City"] = df["City"].str.title()
    
    # Extract unique categories and cities
    category_options = ["All"] + sorted(df["Category"].unique().tolist())
    city_options = ["All"] + sorted(df["City"].unique().tolist())

    # Sidebar Filters
    st.sidebar.header("🔍 Filter Jobs")

    # Apply Filters
    filtered_df = df.copy()

    selected_city = st.sidebar.selectbox("Select City", city_options)
    selected_category = st.sidebar.selectbox("Select Category", category_options)

    if selected_city != "All":
        filtered_df = filtered_df[filtered_df["City"] == selected_city]

    if selected_category != "All":
        filtered_df = filtered_df[filtered_df["Category"].apply(lambda x: selected_category in x)]

    # Pagination
    total_rows = len(filtered_df)
    rows_per_page = 20

    if total_rows == 0:
        st.warning("No jobs found matching your filters.")
        return
    elif total_rows <= rows_per_page:
        total_pages = 1
        page_number = 1  # Show all jobs on a single page
    else:
        total_pages = (total_rows // rows_per_page) + (1 if total_rows % rows_per_page > 0 else 0)
        page_number = st.sidebar.slider("Page", 1, total_pages, 1)

    start_idx = (page_number - 1) * rows_per_page
    end_idx = start_idx + rows_per_page

    st.write(f"Showing {start_idx + 1} - {min(end_idx, total_rows)} of {total_rows} jobs")

    # Display paginated DataFrame
    st.dataframe(filtered_df.iloc[start_idx:end_idx])

    # Job Selection
    job_id_input = st.text_input("Enter the Job ID to proceed:", key="job_id_input")

    if job_id_input:
        if job_id_input in filtered_df["Job ID"].astype(str).values:
            st.success(f"✅ Job ID {job_id_input} selected! Proceeding to the next step...")
            st.session_state.selected_job_id = job_id_input
            st.session_state.page = "Option1_4"
            st.rerun()
        else:
            st.error("⚠️ Invalid Job ID. Please enter a valid ID from the table.")

    # Back to Home
    if st.button("⬅️ Back to Home"):
        st.session_state.page = "Home"
        if "app_initialized" in st.session_state:
            del st.session_state.app_initialized
        st.rerun()
