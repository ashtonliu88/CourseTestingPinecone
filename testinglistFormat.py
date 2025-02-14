import re
import pandas as pd

def extract_courses(requirements_str):
    """Extracts prerequisite courses from a string, grouping them correctly."""
    if pd.isna(requirements_str) or "Prerequisite(s):" not in requirements_str:
        return []  # No prerequisites
    
    # Remove the "Prerequisite(s):" prefix
    requirements_str = requirements_str.replace("Prerequisite(s):", "").strip()

    # Define course code pattern (e.g., CSE 12, MATH 19B, etc.)
    course_pattern = r'\b[A-Z]{2,4} \d+[A-Z]?\b'  

    # Split into logical prerequisite groups
    groups = [group.strip() for group in re.split(r';|\sand\s', requirements_str) if group.strip()]
    prerequisites = []

    for group in groups:
        found_courses = re.findall(course_pattern, group)
        if found_courses:
            prerequisites.append(found_courses)
    
    return prerequisites

requirements = "Prerequisite(s): CSE 20 or BME 160; and MATH 3 or MATH 11A or MATH 19A or AM 3 or AM 11A or ECON 11A, or a score of 400 or higher on the mathematics placement examination (MPE)".replace(",", "")

# prerequisites = parse_prerequisites(requirements)
# print(prerequisites)

# taken = ["CSE 20", "MATH 3"]

# def can_take_course(taken, prerequisites):
#     for group in prerequisites:
#         if not any(course in taken for course in group):
#             return False, group
#     return True, None 

# eligible, missing_group = can_take_course(taken, prerequisites)

# if eligible:
#     print("You can take the class!")
# else:
#     print(f"You cannot take the class because you are missing one of: {missing_group}")

file_path = "testspread.csv"  # Change this to your actual file path
df = pd.read_csv(file_path)

# Extract prerequisites and store in a new column
df["Parsed Prerequisites"] = df["Enrollment Requirements"].apply(extract_courses)
# Delete the "Enrollment Requirements" column
df.drop(columns=["Enrollment Requirements"], inplace=True)
# Save the modified CSV
output_file_path = "classes_parsed.csv"
df.to_csv(output_file_path, index=False)

print(f"Processed CSV saved as {output_file_path}")