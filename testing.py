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

def limit_courses(courses, max_courses=50):
    """Limits the number of courses sent to the LLM to avoid exceeding token limits."""
    return courses.sample(n=min(len(courses), max_courses), random_state=42)

def filter_courses(df, student_history, next_quarter):
    """Filters courses based on availability, prerequisites, and next quarter."""
    # df = df[df['Quarter Offered'] == next_quarter]
    # df = df[df['Available Seats'] > 0]
    # df = df[~df['Class name'].isin(student_history)]
    # print(df)
    return df

def generate_schedule(courses, model="gpt-4-turbo"):
    """Uses an LLM to generate a 3-class schedule with summarized input."""
    
    course_list = "\n".join(
        f"{row['Class name']} ({row['Credits']} credits) - {row['General education']}" 
        for _, row in courses.iterrows()
    )
    
    prompt = f"""
    Here is a list of available courses for next quarter:
    
    {course_list}
    
    Pick 3 courses that provide a balanced schedule based on variety, workload, and prerequisites.
    """

    response = openai_client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are an expert academic advisor."},
            {"role": "user", "content": prompt},
        ],
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
    limited_courses = limit_courses(filtered_courses)
    schedule = generate_schedule(limited_courses)
    
    print("Suggested Schedule:")
    print(schedule)

if __name__ == "__main__":
    main()
