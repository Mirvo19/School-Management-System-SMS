
import os

def calculate_grade(percentage):
    """Calculates the grade based on percentage."""
    if percentage >= 90:
        return 'A'
    elif percentage >= 80:
        return 'B'
    elif percentage >= 70:
        return 'C'
    elif percentage >= 60:
        return 'D'
    elif percentage >= 50:
        return 'E'
    else:
        return 'F'

def calculate_gpa(percentage):
    """Calculates GPA on a 4.0 scale based on percentage."""
    if percentage >= 90:
        return 4.0
    elif percentage >= 80:
        return 3.6
    elif percentage >= 70:
        return 3.2
    elif percentage >= 60:
        return 2.8
    elif percentage >= 50:
        return 2.4
    else:
        return 0.0

def get_valid_float(prompt, min_val, max_val):
    """Prompts user for input and validates it's a float within range."""
    while True:
        try:
            value = float(input(prompt))
            if min_val <= value <= max_val:
                return value
            else:
                print(f"Invalid input. Please enter a value between {min_val} and {max_val}.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def main():
    print("--- Student Result Calculator ---")
    
    students = []
    subjects = ["Math", "Science", "English", "Computer", "History"]
    
    while True:
        try:
            num_students = int(input("Enter the number of students: "))
            if num_students > 0:
                break
            print("Please enter a positive integer.")
        except ValueError:
            print("Invalid input. Please enter an integer.")

    print(f"\nEntering data for {num_students} students.")
    print("Marks: Theory (Max 75), Internal (Max 25)")
    
    for i in range(num_students):
        print(f"\nStudent {i+1}:")
        name = input("Enter Student Name: ").strip()
        
        student_data = {
            "name": name,
            "marks": {},
            "total_marks": 0
        }
        
        for subject in subjects:
            print(f"  {subject}:")
            theory = get_valid_float(f"    Theory (0-75): ", 0, 75)
            internal = get_valid_float(f"    Internal (0-25): ", 0, 25)
            
            total_subject_marks = theory + internal
            student_data["marks"][subject] = {
                "theory": theory,
                "internal": internal,
                "total": total_subject_marks
            }
            student_data["total_marks"] += total_subject_marks
            
        student_data["percentage"] = student_data["total_marks"] / len(subjects)
        student_data["grade"] = calculate_grade(student_data["percentage"])
        student_data["gpa"] = calculate_gpa(student_data["percentage"])
        
        students.append(student_data)

    # Class Statistics
    if not students:
        print("No student data entered.")
        return

    # Topper
    topper = max(students, key=lambda x: x["total_marks"])
    
    # Subject High Scores
    subject_highs = {}
    for subject in subjects:
        highest_mark = 0
        scorer = ""
        for student in students:
            if student["marks"][subject]["total"] > highest_mark:
                highest_mark = student["marks"][subject]["total"]
                scorer = student["name"]
        subject_highs[subject] = (scorer, highest_mark)
        
    # Class Average
    total_class_percentage = sum(s["percentage"] for s in students)
    class_average = total_class_percentage / len(students)

    # Output Formatting
    output_lines = []
    output_lines.append("\n" + "="*80)
    output_lines.append(f"{'STUDENT RESULT REPORT':^80}")
    output_lines.append("="*80)
    
    # Header
    header = f"{'Name':<20} | " + " | ".join([f"{s[:3]:<5}" for s in subjects]) + f" | {'Total':<6} | {'%':<5} | {'Grd':<3} | {'GPA':<4}"
    output_lines.append(header)
    output_lines.append("-" * len(header))
    
    # Student Rows
    for s in students:
        marks_str = " | ".join([f"{s['marks'][sub]['total']:<5.1f}" for sub in subjects])
        row = f"{s['name']:<20} | {marks_str} | {s['total_marks']:<6.1f} | {s['percentage']:<5.1f} | {s['grade']:<3} | {s['gpa']:<4.1f}"
        output_lines.append(row)
    
    output_lines.append("-" * len(header))
    
    # Statistics Section
    output_lines.append("\n" + "="*80)
    output_lines.append(f"{'CLASS STATISTICS':^80}")
    output_lines.append("="*80)
    output_lines.append(f"Class Topper: {topper['name']} with {topper['total_marks']} marks ({topper['percentage']:.1f}%)")
    output_lines.append(f"Class Average Percentage: {class_average:.1f}%")
    output_lines.append("\nSubject High Scores:")
    for subject, (name, score) in subject_highs.items():
        output_lines.append(f"  {subject:<10}: {score:<5.1f} ({name})")
    
    output_str = "\n".join(output_lines)
    
    # Print to Console
    print(output_str)
    
    # Save to File
    filename = "class_result_report.txt"
    with open(filename, "w", encoding='utf-8') as f:
        f.write(output_str)
    
    print(f"\nReport saved to '{os.path.abspath(filename)}'")

if __name__ == "__main__":
    main()
