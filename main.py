import pandas as pd
from openai import OpenAI # Change this if using a different LLM

from dotenv import load_dotenv
import os
import re
load_dotenv()

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def load_courses(csv_path):
    """Loads course data from a CSV file."""
    df = pd.read_csv(csv_path)
    return df

def limit_courses(courses, max_courses=50):
    """Limits the number of courses sent to the LLM to avoid exceeding token limits."""
    return courses.sample(n=min(len(courses), max_courses), random_state=42)

def filter_courses(df, student_history, required_courses, required_ges):
    """Filters courses based on availability, prerequisites, and next quarter."""
    # df = df[df['Quarter Offered'] == next_quarter]
    # df = df[df['Available Seats'] > 0]
    df = df[df['Course Code'].str.split(' - ').str[0].isin(required_courses) | df['General education'].isin(required_ges)]
    df = df[~df['Course Code'].str.split(' - ').str[0].isin(student_history)]
    return df

def extract_prerequisites(df):
    """Extracts course codes and their prerequisites into a separate DataFrame."""
    prerequisites = df[['Course Code', 'Enrollment Requirements']].dropna()
    prerequisites['Course Code'] = prerequisites['Course Code'].str.split(' - ').str[0]
    return prerequisites

def generate_schedule(courses, student_history, ge_history, prerequisites, model="gpt-4o"):
    """Uses an LLM to generate a 3-class schedule with summarized input."""
    
    course_list = "\n".join(
        f"{row.to_dict()}" 
        for _, row in courses.iterrows()
    )
    
    prompt = f"""
    Here is a list of available courses for next quarter:
    
    {course_list}
    
    The student has only taken the following courses:
    {", ".join(student_history)}

    The student has taken the following general education courses: 
    {", ".join(ge_history)}

    
    
    
    The prerequisites for the courses are as follows:
    {prerequisites.to_string(index=False)}

    DO NOT RECOMMEND COURSES THAT THE STUDENT DOES NOT MEET THE PREREQUISITES FOR.

    
    Pick at least 3 classes that provide a balanced schedule based on variety, workload, and prerequisites and which completes their general education in a timely fashion.
    BE SURE TO INCLUDE THE REASON

    do not include classes that the student has general education credit for.
    Pick at most one general education course.
    Prioritize courses that are prerequisites for future courses.
    Ensure that the student meets all prerequisites for the selected courses.
    Do not include courses that the student has already taken.
    Do not recommend classes that require prerequisites that the student will take with the courses.
    Additionally, show which class and their times needs to be selected to provide a balanced schedule.
    If a class has discussion or lab sections, pick one that will be best for their schedule.
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


def get_student_history_ges(df, student_history):
    """Searches for the general education requirements of the student's history classes."""
    ges = df[df['Course Code'].str.split(' - ').str[0].isin(student_history)]['General education'].dropna().unique().tolist()
    return ges

def main():
    csv_path = os.path.join(os.path.dirname(__file__), "testspread.csv")
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found at path: {csv_path}")
    
    df = load_courses(csv_path)
    student_history = ["CSE 20", "MATH 19A"]
    ge_history = get_student_history_ges(df, student_history)

    required_courses = [
        "MATH 19A", "MATH 19B", "MATH 23A", "CSE 20", "CSE 30", "CSE 13S", "CSE 16", "CSE 12", "CSE 101", "CSE 102", "CSE 103", "CSE 107",
        "CSE 120", "CSE 130", "ECE 30", "CSE 114A"
    ]
    required_ges = ["CC", "ER", "IM", "MF", "SI", "SR", "TA", "C", "DC", "PE", "PR"]
 

    filtered_courses = filter_courses(df, student_history, required_courses, required_ges)
    prerequisites = extract_prerequisites(filtered_courses)
    # limited_courses = limit_courses(filtered_courses)
    schedule = generate_schedule(filtered_courses, student_history=student_history, ge_history=ge_history, prerequisites=prerequisites)
    
    print("Suggested Schedule:")
    print(schedule)

if __name__ == "__main__":
    main()
