import csv
from pymongo import MongoClient
from dotenv import load_dotenv
import os
load_dotenv()
# MongoDB connection details
mongo_uri = os.getenv("MONGO_URI")

mongo_db_name = 'classes'
mongo_collection_name = 'courseInfo'

# CSV file path
csv_file_path = 'classes_parsed.csv'

def store_csv_to_mongodb(csv_file_path, mongo_db_name, mongo_collection_name):
    # Connect to MongoDB
    client = MongoClient(mongo_uri)
    db = client[mongo_db_name]
    collection = db[mongo_collection_name]

    # Read CSV file and insert data into MongoDB
    with open(csv_file_path, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            collection.insert_one(row)

    print(f"Data from {csv_file_path} has been stored in MongoDB collection {mongo_collection_name}.")

if __name__ == "__main__":
    store_csv_to_mongodb(csv_file_path, mongo_db_name, mongo_collection_name)