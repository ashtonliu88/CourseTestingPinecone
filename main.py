import json
import pinecone
from openai import OpenAI
from pinecone import Pinecone, ServerlessSpec, PodSpec
from dotenv import load_dotenv
import os
load_dotenv()
# Initialize clients
pinecone_client = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

index_name = "course-catalog"
index = pinecone_client.Index(index_name)
def search_courses():
    while True:
        query = input("Type in what you're looking for in a class (or type 'exit'): ")
        
        if query.lower() == 'exit':
            break

        response = openai_client.embeddings.create(
            input=query,
            model="text-embedding-3-small"
        )
        query_embedding = response.data[0].embedding

        results = index.query(
            vector=query_embedding,
            top_k=3,
            include_metadata=True
        )

        print("\nSuggested courses to take:")
        for match in results['matches']:
            print(f"{match['id']} - {match['metadata']['title']}")
            print(f"Similarity score: {match['score']:.2f}\n")

if __name__ == "__main__":
    search_courses()