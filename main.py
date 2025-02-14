import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv
import os
from pymongo import MongoClient
load_dotenv()

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_mongo_client():
    mongo_uri = os.getenv("MONGO_URI")
    return MongoClient(mongo_uri)

def load_courses_from_mongo(db_name, collection_name):
    client = get_mongo_client()
    db = client[db_name]
    collection = db[collection_name]
    courses = pd.DataFrame(list(collection.find()))
    return courses


def limit_courses(courses, max_courses=300):
    return courses.sample(n=min(len(courses), max_courses), random_state=42)

def filter_courses(df, student_history, required_courses, required_ges):

    df = df[
        df['Course Code'].str.split(' - ').str[0].isin(required_courses) | 
        df['General education'].isin(required_ges) |
        df['Course Code'].str.contains(r'CSE 1[0-6][0-9]')
    ]
    df = df[~df['Course Code'].str.split(' - ').str[0].isin(student_history)]
    return df

def extract_prerequisites(df):
    prerequisites = df[['Course Code', 'Parsed Prerequisites']].dropna()
    prerequisites['Course Code'] = prerequisites['Course Code'].str.split(' - ').str[0]
    return prerequisites

def generate_schedule(courses, student_history, ge_history, required_courses, upper_electives_taken, upper_electives_needed, prerequisites, model="chatgpt-4o-latest"):
    
    course_list = "\n".join(
        f"{row.to_dict()}" 
        for _, row in courses.iterrows()
    )

    prompt = f"""
    Here is a list of available courses for next quarter:
    
    {course_list}
    
    The student has only taken the following courses:
    {student_history}

    The student has taken the following general education courses: 
    {ge_history}
    REMOVE GENERAL EDUCATION CLASSES FOR CONSIDERATION FROM THE COURSE LIST THAT THE STUDENT HAS ALREADY TAKEN.
    DO NOT RECOMMEND COURSES THAT THE STUDENT DOES NOT HAVE THE PREREQUISITES FOR IN THEIR HISTORY.
    The prerequisites for the courses are as follows:
    
    {prerequisites}

    REMOVE CLASSES FOR CONSIDERATION FROM THE COURSE LIST THAT THE STUDENT DOES NOT HAVE THE PREREQUISITES FOR.

    These are courses that the student still needs to take:

    {required_courses}
    prioritize courses that are prerequisites for future courses.
    
    This is the number of upper division electives the student has taken:
    {upper_electives_taken}
    Upper electives will be classes with course codes 100+.
    This is the number of upper division electives the student needs to take:
    {upper_electives_needed}

    Pick at least 3 classes that provide a balanced schedule based on variety, workload, and prerequisites and which completes their general education in a timely fashion.
    BE SURE TO INCLUDE THE REASON

    PICK AT LEAST ONE GENERAL EDUCATION COURSE THAT THE STUDENT HAS NOT TAKEN YET IF THE STUDENT HAS NOT TAKEN ALL GENERAL EDUCATION COURSES.
    Do not include classes that the student has general education credit for.
    
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
    ges = df[df['Course Code'].str.split(' - ').str[0].isin(student_history)]['General education'].dropna().unique().tolist()
    return ges

def can_take_course(taken, prerequisites):
    for group in prerequisites:
        if not any(course in taken for course in group):
            return False
        
    return True, None 
def main():
    student_history = ["MATH 19A", "CSE 20", "PHYS 1B", 'MATH 19B', "CSE 30", "HAVC 135H", "MATH 21", "CSE 16", "HIS 74A",
                       "MATH 23A", "CSE 12", "HAVC 64"]
    major = input("Enter your major: ")
    year = input("Enter the year of admission: ")
    db_name = "nextQuarter"
    collection_name = "classInfo"
    client = get_mongo_client()
    db = client[db_name]
    collection = db[collection_name]
    data = list(collection.find())

    

    eligible_courses = []
    
    for document in data[:450]:
        if 'Parsed Prerequisites' in document:
            prerequisites = document['Parsed Prerequisites']
            if isinstance(prerequisites, str):
                prerequisites = eval(prerequisites)

            eligible = can_take_course(student_history, prerequisites)

            if eligible:
                eligible_courses.append(document)

    eligible_courses_df = pd.DataFrame(eligible_courses)

    ge_history = get_student_history_ges(eligible_courses_df, student_history)

    courses = load_courses_from_mongo("university", "majors")

    major_data = courses[(courses['major'] == major) & (courses['admission_year'] == year)]
    if major_data.empty:
        raise ValueError(f"No data found for major: {major} and year: {year}")
    
    required_courses = major_data['required_courses'].iloc[0]

    courses_left = [course for course in required_courses if course not in student_history]
    
    required_ges = ["CC", "ER", "IM", "MF", "SI", "SR", "TA", "C", "DC", "PE", "PR"]
 
    upper_electives_taken = 0
    upper_electives_needed = 4

    filtered_courses = filter_courses(eligible_courses_df, student_history, required_courses, required_ges)
    prerequisites = extract_prerequisites(filtered_courses)
    limited_courses = limit_courses(filtered_courses)
    schedule = generate_schedule(limited_courses, student_history=student_history, 
                                 ge_history=ge_history, required_courses=courses_left, 
                                 upper_electives_taken = upper_electives_taken, upper_electives_needed = upper_electives_needed,
                                 prerequisites=prerequisites)
    
    print("Suggested Schedule:")
    print(schedule)


if __name__ == "__main__":
    main()
