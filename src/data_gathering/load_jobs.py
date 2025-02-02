import os
import sys
import logging
import pymongo
import pandas as pd
from dotenv import load_dotenv, find_dotenv

# Configuring logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Loading environment variables from .env file
load_dotenv(find_dotenv())

# Getting MongoDB connection string
connection_string = os.environ.get("url")
if not connection_string:
    logging.error("MongoDB connection string is missing. Set the 'url' environment variable.")
    sys.exit(1)

# MongoDB connection with proper error handling
try:
    with pymongo.MongoClient(connection_string, serverSelectionTimeoutMS=5000) as client:
        # Checking connection
        client.admin.command("ping")
        logging.info("Successfully connected to MongoDB Atlas! 🎉")

        # Selecting database and collection
        db = client.jobsDB
        collection = db.jobsCollection

        # Clearing the collection before inserting new data
        deleted_count = collection.delete_many({}).deleted_count
        logging.info(f"Deleted {deleted_count} existing documents from 'jobsCollection'.")

        # Reading the Excel file
        excel_file_path = "Jobs Data.xlsx"
        if not os.path.exists(excel_file_path):
            logging.error(f"Excel file not found: {excel_file_path}")
            sys.exit(1)

        try:
            data = pd.read_excel(excel_file_path)
            logging.info(f"Excel file '{excel_file_path}' loaded successfully.")
        except Exception as e:
            logging.error(f"Error reading the Excel file: {e}")
            sys.exit(1)

        # Converting DataFrame to a list of dictionaries
        data_dict = data.to_dict(orient="records")
        if not data_dict:
            logging.warning("Excel file is empty, no data inserted.")
        else:
            # Inserting the new data into MongoDB
            try:
                collection.insert_many(data_dict, ordered=False)
                logging.info(f"{len(data_dict)} documents inserted into 'jobsCollection'.")
            except pymongo.errors.BulkWriteError as bwe:
                logging.error(f"Error inserting documents: {bwe.details}")
            except Exception as e:
                logging.error(f"Unexpected error while inserting documents: {e}")
                sys.exit(1)

        # Verify inserted data
        logging.info("Verifying inserted documents:")
        for doc in collection.find({}, {"_id": 0}):  # Hide `_id` for cleaner output
            logging.info(doc)

except pymongo.errors.ServerSelectionTimeoutError:
    logging.error("Could not connect to MongoDB. Check your connection string and network.")
    sys.exit(1)
except Exception as e:
    logging.error(f"Unexpected error: {e}")
    sys.exit(1)
