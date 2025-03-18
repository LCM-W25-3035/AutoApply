import pymongo 
# testin carol pull
# MongoDB Connection
MONGO_URI = "mongodb+srv://DavidRocha:davidoscar@capstone.9ajag.mongodb.net/?retryWrites=true&w=majority&appName=Capstone"
MONGO_DB_NAME = "jobsDB"
MONGO_JOBS_COLLECTION = "jobsCollection"

client_mongo = pymongo.MongoClient(MONGO_URI)
db = client_mongo[MONGO_DB_NAME]
collection = db[MONGO_JOBS_COLLECTION]

# Load jobs from MongoDB
jobs_data = list(collection.find({}).limit(5))  # Retrieve everything
