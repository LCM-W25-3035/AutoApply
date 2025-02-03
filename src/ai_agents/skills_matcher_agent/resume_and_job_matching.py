import os
import json
import numpy as np
import pymongo
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Define Input and Output File Paths
input_filepath = os.path.join("src", "ai_agents", "resume_analyzer_agent", "analyzer_output_3.json")
output_filepath = os.path.join("src", "ai_agents", "skills_matcher_agent", "resume_3_matched_jobs.json")

# Load Embedding Model
embedding_model = SentenceTransformer("all-mpnet-base-v2")

# MongoDB Connection
MONGO_URI = "mongodb+srv://DavidRocha:davidoscar@capstone.9ajag.mongodb.net/?retryWrites=true&w=majority&appName=Capstone"
MONGO_DB_NAME = "jobsDB"
MONGO_COLLECTION_NAME = "jobsCollection"

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
technical_skills = []
for category, skills in resume_data['skills_analysis']['technical_skills']['categories'].items():
    technical_skills.extend(skills)

technical_skills.extend(resume_data['skills_analysis']['technical_skills']['other_skills'])

years_experience = resume_data['skills_analysis']['years_of_experience']
experience_level = resume_data['skills_analysis']['experience_level']
education_level = resume_data['skills_analysis']['education']['level']
education_field = resume_data['skills_analysis']['education']['field']
domain_expertise = resume_data['skills_analysis']['domain_expertise']
key_achievements = resume_data['skills_analysis']['key_achievements']

# Generate Structured Resume Text for Embedding
resume_text = f"{', '.join(technical_skills)}. " \
              f"{experience_level}-level experience with {years_experience} years in the field. " \
              f"Holds a {education_level} in {education_field}. " \
              f"Expertise in {', '.join(domain_expertise)}. "

if key_achievements:
    resume_text += f"Key Achievements: {'. '.join(key_achievements)}."

print("\nOptimized Resume Text for Embedding:", resume_text)

# Generate Resume Embedding (Without Storing in MongoDB)
resume_embedding = embedding_model.encode(resume_text).reshape(1, -1)  # Convert to 2D array

print("\nResume Embedding Generated (Ready for Matching)")

# Retrieve All Job Embeddings from MongoDB
jobs = list(collection.find({"embedding": {"$exists": True}}))

if not jobs:
    print("No job embeddings found in MongoDB.")
    exit()

# Compute Similarity Scores
job_matches = []
for job in jobs:
    job_embedding = np.array(job["embedding"]).reshape(1, -1)  # Convert to 2D array
    similarity_score = cosine_similarity(resume_embedding, job_embedding)[0][0]

    job_matches.append({
        "job_title": job["Job Title"],
        "company": job["Company Name"],
        "similarity_score": round(similarity_score, 4),
        "job_url": job.get("job url", "N/A")
    })

# Sort Jobs by Highest Similarity Score
top_matches = sorted(job_matches, key=lambda x: x["similarity_score"], reverse=True)[:10]

# Save Top 10 Job Matches as JSON
with open(output_filepath, "w", encoding="utf-8") as json_file:
    json.dump({"matched_jobs": top_matches}, json_file, ensure_ascii=False, indent=4)

print(f"\nTop 10 Job Matches saved to '{output_filepath}'.")