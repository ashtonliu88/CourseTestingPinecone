import json
import pinecone
from openai import OpenAI
from pinecone import Pinecone, ServerlessSpec, PodSpec
from dotenv import load_dotenv
import os
load_dotenv()

#clients
pinecone_client = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

with open('reformatted_classes.json', 'r') as f:
    courses = json.load(f)

use_serverless = True

if use_serverless:
    #deploy serverless
    spec = ServerlessSpec(cloud='aws', region='us-east-1')
else:
    spec = PodSpec(environment=environment)

index_name = "class-reformat"
if index_name not in pinecone_client.list_indexes():
    pinecone_client.create_index(
        name=index_name, 
        dimension=1536,
        spec = spec)
else:
    print("Index already exists, skipping creation")
    
index = pinecone_client.Index(index_name)
for course in courses:
    response = openai_client.embeddings.create(
        input=course["description"],
        model="text-embedding-3-small"
    )
    vector = {
        "id": course["class_name"],
        "values": response.data[0].embedding,
        "metadata": {
            "class_name": course["class_name"],
            "quarter_offered": course.get("quarters_offered", ""),
            "career": course.get("career", ""),
            "grading": course.get("grading", ""),
            "class_number": course.get("class_number", ""),
            "type": course.get("type", ""),
            "instruction_mode": course.get("instruction_mode", ""),
            "credits": course.get("credits", ""),
            "general_education": course.get("general_education", ""),
            "status": course.get("status", ""),
            "available_seats": course.get("available_seats", ""),
            "enrollment_capacity": course.get("enrollment_capacity", ""),
            "enrolled": course.get("enrolled", ""),
            "wait_list_capacity": course.get("wait_list_capacity", ""),
            "wait_list_total": course.get("wait_list_total", ""),
            "description": course.get("description", ""),
            "enrollment_requirements": course.get("enrollment_requirements", ""),
            "class_notes": course.get("class_notes", ""),
            "meeting_information": course.get("meeting_information", ""),
            "associated_discussion_sections_or_labs": course.get("associated_discussion_sections_or_labs", ""),
        }
    }
    index.upsert(vectors=[vector])

print("Indexing complete")