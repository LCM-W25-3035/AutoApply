import os
import json
import numpy as np
import pymongo
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv

# Define Input and Output File Paths
input_filepath = os.path.join("src", "ai_agents", "resume_analyzer_agent", "analyzer_output_5.json")
output_filepath = os.path.join("src", "ai_agents", "resume_jobs_matcher_agent", "matched_jobs_for_resume_5.json")

# Load Embedding Model
embedding_model = SentenceTransformer("all-mpnet-base-v2")

# Load .env file
load_dotenv()

# Get MongoDB connection details from environment variables
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")
MONGO_COLLECTION_NAME = os.getenv("MONGO_COLLECTION_NAME")

if not MONGO_URI or not MONGO_DB_NAME or not MONGO_COLLECTION_NAME:
    print("Error: Missing MongoDB credentials in the .env file.")
    exit()

# MongoDB Connection
client = pymongo.MongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]
collection = db[MONGO_COLLECTION_NAME]

try:
    with open(input_filepath, "r", encoding="utf-8") as f:
        resume_data = json.load(f)
except FileNotFoundError:
    print(f"Error: File not found at {input_filepath}")
    exit()

# Extract Resume Data
skills_analysis = resume_data.get('skills_analysis', {})

# Extract technical skills (Handle list structure)
technical_skills = []

categories = resume_data['skills_analysis']['technical_skills'].get('categories', {})

if isinstance(categories, dict):  # If categories is a dictionary (expected case)
    for category, skills in categories.items():
        technical_skills.extend(skills)
elif isinstance(categories, list):  # If categories is a list (unexpected but possible)
    for category_dict in categories:
        if isinstance(category_dict, dict):  # Ensure it's a dictionary
            for skills_list in category_dict.values():
                technical_skills.extend(skills_list)

# Include "other_skills" if available
technical_skills.extend(resume_data['skills_analysis']['technical_skills'].get('other_skills', []))

years_experience = skills_analysis.get('years_of_experience', "Unknown")
experience_level = skills_analysis.get('experience_level', "Unknown")
education_level = skills_analysis.get('education', {}).get('level', "Unknown")
education_field = skills_analysis.get('education', {}).get('field', "Unknown")
domain_expertise = skills_analysis.get('domain_expertise', [])
key_achievements = skills_analysis.get('key_achievements', [])
job_titles = skills_analysis.get('job_titles', [])  # Extracted job titles from work history
professional_summary = skills_analysis.get('professional_summary', "No summary available.")

# Extract Must-have Skills from MongoDB Job Listings
jobs = list(collection.find({"Embedding": {"$exists": True}}))
must_have_skills_set = set()

for job in jobs:
    must_have_skills = job.get("Must-have Skills", [])
    if isinstance(must_have_skills, str):
        must_have_skills = must_have_skills.split(", ")  # Convert string to list
    must_have_skills_set.update(must_have_skills)

# Weight must-have skills higher
weighted_skills = []
for skill in technical_skills:
    if skill in must_have_skills_set:
        weighted_skills.extend([skill] * 3)  # Triple weight for must-have skills
    else:
        weighted_skills.append(skill)

# Extract job title dynamically from job history or domain expertise
job_title = job_titles[0] if job_titles else (domain_expertise[0] if domain_expertise else "Unknown Role")

# Generate Structured Resume Text for Embedding
resume_text = f"{professional_summary}. " \
              f"Previous roles: {', '.join(job_titles)}. " \
              f"{experience_level}-level experience with {years_experience} years. " \
              f"Holds a {education_level} in {education_field}. " \
              f"Expertise in {', '.join(domain_expertise)}. " \
              f"Skills: {', '.join(weighted_skills)}."

if key_achievements:
    resume_text += f" Key Achievements: {'. '.join(key_achievements)}."

print("\nOptimized Resume Text for Embedding:", resume_text)

# Generate Resume Embedding (Without Storing in MongoDB)
resume_embedding = embedding_model.encode(resume_text).reshape(1, -1)  # Convert to 2D array

print("\nResume Embedding Generated (Ready for Matching)")

# Retrieve All Job Embeddings from MongoDB
jobs = list(collection.find({"Embedding": {"$exists": True}}))

if not jobs:
    print("No job embeddings found in MongoDB.")
    exit()

# Compute Similarity Scores
job_matches = []
for job in jobs:
    job_embedding = np.array(job["Embedding"]).reshape(1, -1)  # Convert to 2D array
    similarity_score = cosine_similarity(resume_embedding, job_embedding)[0][0]

    job_matches.append({
        "job_title": job.get("Job Title", "N/A"),
        "company": job.get("Company Name", "N/A"),
        "must_have_skills": job.get("Must-have Skills", "N/A"),
        "experience_level": job.get("Experience Level", "N/A"),
        "education_level": job.get("Education level", "N/A"),
        "similarity_score": round(similarity_score, 4),
        "job_url": job.get("job url", "N/A")
    })

# Sort Jobs by Highest Similarity Score
top_matches = sorted(job_matches, key=lambda x: x["similarity_score"], reverse=True)[:10]

# Save Top 10 Job Matches as JSON
with open(output_filepath, "w", encoding="utf-8") as json_file:
    json.dump({"matched_jobs": top_matches}, json_file, ensure_ascii=False, indent=4)

print(f"\nTop 10 Job Matches saved to '{output_filepath}'.")

# Reference
# (OpenAI first prompt, 2025): How can we match a resume to job listings using embeddings?
# (OpenAI last prompt, 2025): Can you show an example of matching a resume to job listings using embeddings?