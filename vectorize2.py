import csv
import json

# Read the CSV file and reformat it
def reformat_csv(file_path):
    classes = []
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Reformat each row into a dictionary
            class_data = {
                "class_name": row["Class name"],
                "quarter_offered": row["Quarter Offered"],
                "career": row["Career"],
                "grading": row["Grading"],
                "class_number": int(row["Class Number"]) if row["Class Number"] else 0,
                "type": row["Type"],
                "instruction_mode": row["Instruction Mode"],
                "credits": int(''.join(filter(str.isdigit, row["Credits"]))) if row["Credits"] else 0,
                "general_education": row["General education"],
                "status": row["Status"],
                "available_seats": int(row["Available Seats"]) if row["Available Seats"] else 0,
                "enrollment_capacity": int(row["Enrollment Capacity"]) if row["Enrollment Capacity"] else 0,
                "enrolled": int(row["Enrolled"]) if row["Enrolled"] else 0,
                "wait_list_capacity": int(row["Wait List Capacity"]) if row["Wait List Capacity"] else 0,
                "wait_list_total": int(row["Wait List Total"]) if row["Wait List Total"] else 0,
                "description": row["Description"],
                "enrollment_requirements": row["Enrollment Requirements"],
                "class_notes": row["Class Notes"],
                "meeting_information": row["Meeting Information"],
                "associated_discussion_sections_or_labs": row["Associated Discussion Sections or Labs"]
            }
            classes.append(class_data)
    return classes

# Example usage
file_path = "classes.csv"
reformatted_classes = reformat_csv(file_path)
print(reformatted_classes[0])
# Write the reformatted data to a JSON file
output_file_path = "reformatted_classes.json"
with open(output_file_path, mode='w', encoding='utf-8') as json_file:
    json.dump(reformatted_classes, json_file, ensure_ascii=False, indent=4)

print(f"Data has been written to {output_file_path}")