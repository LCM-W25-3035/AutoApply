import streamlit as st
import pymongo
import pandas as pd
import option1

# MongoDB Connection
MONGO_URI="mongodb+srv://DavidRocha:davidoscar@capstone.9ajag.mongodb.net/?retryWrites=true&w=majority&appName=Capstone"
MONGO_DB_NAME="jobsDB"
MONGO_JOBS_COLLECTION="jobsCollection"

client_mongo = pymongo.MongoClient(MONGO_URI)
db = client_mongo[MONGO_DB_NAME]
collection = db[MONGO_JOBS_COLLECTION]

def main():
    st.title("Welcome to AutoApply App")
    st.write("Your all-in-one solution for enhancing and customizing your resume to secure your dream job!")
    
    option = st.radio("What would you like to do?", [
        # "1. Enhance my resume for complete my skills and create cv master",
        "-> Tailor my resume for a specific job opportunity",
        "-> Find the best job matches and optimize my resume accordingly"
    ], index=None)
    
    if option == "-> Tailor my resume for a specific job opportunity":
        option1.run()  # Calls the function from option1.py

    elif option == "-> Find the best job matches and optimize my resume accordingly":
        filter_jobs = st.checkbox("Would you like to filter job listings?")
        
        if filter_jobs:
            locations = [job['_id'] for job in collection.aggregate([
                {"$group": {"_id": "$Location", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ])]
            selected_location = st.selectbox("Choose a location:", ["All"] + locations)
            
            experience_levels = ["Junior", "Semi Senior", "Senior"]
            selected_experience = st.selectbox("Select your experience level:", ["All"] + experience_levels)
            
            it_roles = [job['Role'] for job in collection.find({}, {"Role": 1, "_id": 0})]
            it_roles = list(set(it_roles))
            selected_role = st.selectbox("Select your IT role:", ["All"] + it_roles)
            
            query = {}
            if selected_location != "All":
                query["Location"] = selected_location
            if selected_experience != "All":
                query["ExperienceLevel"] = selected_experience
            if selected_role != "All":
                query["Role"] = selected_role
            
            job_offers = list(collection.find(query))
        else:
            job_offers = list(collection.find())
        
        st.write(f"Total job opportunities available: {len(job_offers)}")
        
        uploaded_cv = st.file_uploader("Upload your resume (PDF or DOCX)", type=["pdf", "docx"])
        if uploaded_cv:
            best_matches = find_best_jobs(uploaded_cv, job_offers)
            st.write("Top 10 Matching Job Opportunities:")
            st.dataframe(best_matches)

if __name__ == "__main__":
    main()