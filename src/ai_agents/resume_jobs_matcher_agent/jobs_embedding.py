import pymongo
import os
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv  # Load environment variables

# Load .env file (stored in the main directory)
load_dotenv()

# Get MongoDB connection details from environment variables
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")
MONGO_COLLECTION_NAME = os.getenv("MONGO_COLLECTION_NAME")

if not MONGO_URI or not MONGO_DB_NAME or not MONGO_COLLECTION_NAME:
    print("Error: Missing MongoDB credentials in the .env file.")
    exit()

# Load Embedding Model
embedding_model = SentenceTransformer("all-mpnet-base-v2")

# MongoDB Connection
client = pymongo.MongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]
collection = db[MONGO_COLLECTION_NAME]

# Fetch Only Jobs That Don't Have an Embedding
jobs = collection.find({"Embedding": {"$exists": False}})

job_count = 0  # Counter for processed jobs

for job in jobs:
    job_id = job["_id"]
    print(f"Processing job: {job.get('Job Title', 'Unknown')} at {job.get('Company Name', 'Unknown')}")

    # Use job description as the main source of information
    job_text = f"{job.get('Job Title', '')} {job.get('Must-have Skills', '')} {job.get('Nice-to-have Skills', '')} {job.get('Job Description', '')}"

    # Generate Embedding
    job_embedding = embedding_model.encode(job_text).tolist()  # Convert numpy array to list

    # Update MongoDB with the new embedding
    collection.update_one({"_id": job_id}, {"$set": {"Embedding": job_embedding}})
    
    job_count += 1  # Increment processed job counter

print(f"\nJob embeddings successfully stored for {job_count} missing jobs in MongoDB!")