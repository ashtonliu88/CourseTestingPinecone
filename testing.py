import pandas as pd
from openai import OpenAI # Change this if using a different LLM

from dotenv import load_dotenv
import os
load_dotenv()

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def load_courses(csv_path):
    """Loads course data from a CSV file."""
    df = pd.read_csv(csv_path)
    return df

def filter_courses(df, student_history, next_quarter):
    """Filters courses based on availability, prerequisites, and next quarter."""
    df = df[df['Quarter Offered'] == next_quarter]
    df = df[df['Available Seats'] > 0]
    df = df[~df['Class name'].isin(student_history)]
    return df

def generate_schedule(courses, model="gpt-4"):
    """Uses an LLM to generate a 3-class schedule."""
    prompt = f"""
    Given the following list of available courses, select a well-balanced set of 3 courses:
    {courses[['Class name', 'Credits', 'General education', 'Meeting Information']].to_string(index=False)}
    Consider variety, credit balance, and prerequisites.
    """
    
    response = openai_client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": "You are an expert academic advisor."},
                  {"role": "user", "content": prompt}]
    )
    
    response_message = response.choices[0].message.content

    return response_message

def main():
    csv_path = os.path.join(os.path.dirname(__file__), "courses.csv")
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found at path: {csv_path}")
    student_history = ["Math 101", "CS 101"]  # Example, should come from user input
    next_quarter = "Spring 2025"
    
    df = load_courses(csv_path)
    filtered_courses = filter_courses(df, student_history, next_quarter)
    schedule = generate_schedule(filtered_courses)
    
    print("Suggested Schedule:")
    print(schedule)

if __name__ == "__main__":
    main()
