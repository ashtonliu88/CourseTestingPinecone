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

with open('merged_courses.json', 'r') as f:
    courses = json.load(f)

use_serverless = True

if use_serverless:
    #deploy serverless
    spec = ServerlessSpec(cloud='aws', region='us-east-1')
else:
    spec = PodSpec(environment=environment)

index_name = "course-scheduler"
if index_name not in pinecone_client.list_indexes():
    pinecone_client.create_index(
        name=index_name, 
        dimension=1536,
        spec = spec)
else:
    print("Index already exists, skipping creation")
    
index = pinecone_client.Index(index_name)
for course in courses:
    if not course["instructors"]:
        continue
    text = f"{course['code']}: {course['title']}"
    response = openai_client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    vector = {
        "id": course["code"],
        "values": response.data[0].embedding,
        "metadata": {
            "title": course["title"],
            "description": course["description"],
            "credits": course["credits"],
            "prerequisites": course["prerequisites"],
            "quarters_offered": course["quarters_offered"],
            "full_text": text
        }
    }
    index.upsert(vectors=[vector])

print("Indexing complete")