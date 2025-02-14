from pymongo import MongoClient
from dotenv import load_dotenv
import os
# Replace with your MongoDB connection string
load_dotenv()
# Connect to MongoDB
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["university"]  # Database name
collection = db["majors"]   # Collection name


def insert_major_data(major, year, required_courses, ge_requirements, upper_electives_needed):
    """Inserts major data into MongoDB."""
    major_data = {
        "major": major,
        "admission_year": year,
        "required_courses": required_courses,
        "ge_requirements": ge_requirements,
        "upper_electives_needed": upper_electives_needed
    }
    
    collection.insert_one(major_data)
    print(f"Inserted data for {major} ({year}) successfully!")


def get_major_data(major, year):
    """Fetches major requirements from MongoDB."""
    result = collection.find_one({"major": major, "admission_year": year}, {"_id": 0})
    return result if result else "No data found"


def update_major_data(major, year, updated_fields):
    """Updates specific fields of a major in MongoDB."""
    update_result = collection.update_one(
        {"major": major, "admission_year": year},
        {"$set": updated_fields}
    )
    
    if update_result.matched_count:
        print(f"Updated {major} ({year}) successfully!")
    else:
        print("No matching record found to update.")


def delete_major_data(major, year):
    """Deletes major data from MongoDB."""
    delete_result = collection.delete_one({"major": major, "admission_year": year})
    
    if delete_result.deleted_count:
        print(f"Deleted {major} ({year}) successfully!")
    else:
        print("No matching record found to delete.")


if __name__ == "__main__":
    # Example: Insert major data
    insert_major_data(
        major="Computer Science",
        year="2023-2024",
        required_courses=[
            "MATH 19A", "MATH 19B", "MATH 23A", "MATH 21", "CSE 20", "CSE 30", "CSE 13S", "CSE 16", "CSE 12", "CSE 101", "CSE 102", "CSE 103", "CSE 107",
        "CSE 120", "CSE 130", "ECE 30", "CSE 114A", "CSE 101M"
        ],
        ge_requirements=["CC", "ER", "IM", "MF", "SI", "SR", "TA", "C", "DC", "PE", "PR"],
        upper_electives_needed=3
    )

    # Example: Fetch and print major data
    major_info = get_major_data("Computer Science", "2022-2023")
    print("Major Data:", major_info)

    # Example: Update major data
    update_major_data("Computer Science", "2022-2023", {"upper_electives_needed": 5})

    # Example: Fetch updated data
    updated_major_info = get_major_data("Computer Science", "2022-2023")
    print("Updated Major Data:", updated_major_info)

    # Example: Delete major data (optional)
    # delete_major_data("Computer Science", "2022-2023")
