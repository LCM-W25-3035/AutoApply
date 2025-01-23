from dotenv import load_dotenv, find_dotenv
import os
import pymongo
import pandas as pd

# Load environment variables from the .env file
load_dotenv(find_dotenv())

# Get the MongoDB connection string from the environment variables
connection_string = os.environ.get("url")

# Connect to the MongoDB client
try:
    client = pymongo.MongoClient(connection_string)
    print("Successfully connected to MongoDB Atlas! 🎉")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    exit()

# Select the database and collection
db = client.jobsDB  # Name of the database
collection = db.jobsCollection  # Name of the collection

# Clear the collection before inserting new data
try:
    collection.delete_many({})  # Deletes all documents in the collection
    print("Existing data in the collection has been cleared.")
except Exception as e:
    print(f"Error clearing the collection: {e}")
    exit()

# Read the Excel file using pandas
excel_file_path = "Jobs Data.xlsx"  # Make sure this file is in the same directory as the script
try:
    data = pd.read_excel(excel_file_path)
    print(f"Excel file '{excel_file_path}' loaded successfully.")
except FileNotFoundError:
    print(f"Excel file not found: {excel_file_path}")
    exit()
except Exception as e:
    print(f"Error reading the Excel file: {e}")
    exit()

# Convert the pandas DataFrame to a list of dictionaries for MongoDB insertion
data_dict = data.to_dict(orient="records")

# Insert the new data into the collection
try:
    collection.insert_many(data_dict)
    print(f"{len(data_dict)} documents have been inserted into the collection 'jobsCollection'.")
except pymongo.errors.BulkWriteError as bwe:
    print(f"Error inserting documents: {bwe.details}")
except Exception as e:
    print(f"Unexpected error while inserting documents: {e}")
    exit()

# Verify the inserted data
print("Documents in the collection:")
try:
    for doc in collection.find():
        print(doc)
except Exception as e:
    print(f"Error retrieving documents from the collection: {e}")
