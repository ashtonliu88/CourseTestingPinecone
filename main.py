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

index_name = "course-scheduler"
index = pinecone_client.Index(index_name)

def llm_parse_courses(input_str):
    """
    Use OpenAI's GPT-4 to extract and standardize course codes from user input.
    Returns a list of course codes in the format 'ABC123'.
    """
    # Improved prompt to ensure valid JSON response
    prompt = f"""
    Extract university course codes from this text, standardizing to format 'ABC123'. 
    Input: "{input_str}"
    
    Return ONLY a valid JSON object with the key "courses" and a list of course codes.
    Examples:
    - Input: "cse 20" → {{"courses": ["CSE20"]}}
    - Input: "math 3 and econ 11a" → {{"courses": ["MATH3", "ECON11A"]}}
    - Input: "Operating Systems" → {{"courses": ["CSE130"]}}
    - Input: "I have no idea what I took" → {{"courses": []}}
    """
    
    try:
        # Call OpenAI API
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        
        # Extract the response content
        response_content = response.choices[0].message.content
        
        # Safely parse the JSON response
        response_json = json.loads(response_content)
        
        # Validate the response format
        if isinstance(response_json, dict) and "courses" in response_json:
            # Remove duplicates by converting to a set and back to a list
            return list(set(response_json["courses"]))
        else:
            print("Error: OpenAI response is not in the expected format.")
            return []
    
    except json.JSONDecodeError:
        print("Error: Invalid JSON response from OpenAI API. Falling back to regex parsing.")
        # Fallback to regex parsing if JSON parsing fails
        return []
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return []
    

if __name__ == "__main__":
    input_1 = input("Enter the courses you have taken: ")
    print(f"Input: {input_1}")
    print(f"Output: {llm_parse_courses(input_1)}")
