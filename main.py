"""Command-line interface for the Student Management System.

Run with:  python main.py
(optional)  python main.py path/to/other_data_file.json
"""

import os
import sys

from manager import StudentManager
from reports import class_statistics, format_statistics, student_report, students_table
from student import FIELD_VALIDATORS, Student
from validators import (
    validate_age,
    validate_department,
    validate_email,
    validate_grade,
    validate_id,
    validate_mark,
    validate_name,
    validate_subject,
)

DEFAULT_DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "students.json")
DEFAULT_SUBJECTS = ["Math", "English", "Physics", "Chemistry", "Computer Science"]


# ---------------------------------------------------------------- input helpers
def ask(prompt, validator):
    """Keep asking until the validator accepts the input."""
    while True:
        try:
            return validator(input(prompt))
        except ValueError as error:
            print(f"  Invalid input: {error}")


def ask_yes_no(prompt):
    while True:
        answer = input(f"{prompt} (y/n): ").strip().lower()
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        print("  Please type y or n.")


def ask_new_id(manager):
    """Ask for a valid ID that is not already used."""
    while True:
        student_id = ask("Student ID (e.g. S009): ", validate_id)
        if manager.find_by_id(student_id):
            print("  That ID is already registered. Please use a different ID.")
        else:
            return student_id


def ask_existing_student(manager):
    """Ask for an ID and return the student, or None if not found."""
    student = manager.find_by_id(input("Enter student ID: "))
    if student is None:
        print("No student found with that ID.")
    return student


# ---------------------------------------------------------------- menu actions
def add_student(manager):
    print("\n--- Add New Student ---")
    student_id = ask_new_id(manager)
    name = ask("Full name: ", validate_name)
    age = ask("Age: ", validate_age)
    email = ask("Email: ", validate_email)
    department = ask("Department: ", validate_department)

    marks = {}
    for subject in DEFAULT_SUBJECTS:
        marks[subject] = ask(f"Marks in {subject} (0-100): ", validate_mark)
    while ask_yes_no("Add another subject?"):
        subject = ask("Subject name: ", validate_subject)
        if subject in marks:
            print("  That subject is already entered.")
            continue
        marks[subject] = ask(f"Marks in {subject} (0-100): ", validate_mark)

    manager.add_student(Student(student_id, name, age, email, department, marks))
    print("Student added and saved successfully.")


def show_all_students(manager):
    print("\n--- All Registered Students ---")
    print(students_table(manager.students))
    print(f"Total: {len(manager.students)} student(s)")


def search_student(manager):
    print("\n--- Search Student ---")
    choice = input("Search by 1) ID  2) Name : ").strip()
    if choice == "1":
        student = manager.find_by_id(input("Enter student ID: "))
        results = [student] if student else []
    elif choice == "2":
        results = manager.search_by_name(input("Enter name (or part of it): "))
    else:
        print("Invalid choice.")
        return
    print(students_table(results))


def update_student(manager):
    print("\n--- Update Student ---")
    student = ask_existing_student(manager)
    if student is None:
        return
    print("What do you want to update?")
    print("  1) Name  2) Age  3) Email  4) Department  5) A subject mark")
    choice = input("Choose: ").strip()
    fields = {"1": "name", "2": "age", "3": "email", "4": "department"}

    if choice in fields:
        field = fields[choice]
        value = ask(f"New {field}: ", FIELD_VALIDATORS[field])
        manager.update_student(student.student_id, field, value)
    elif choice == "5":
        subject = ask("Subject to change: ", validate_subject)
        mark = ask(f"New marks for {subject} (0-100): ", validate_mark)
        manager.update_mark(student.student_id, subject, mark)  # error if subject unknown
    else:
        print("Invalid choice.")
        return
    print("Student updated and saved successfully.")


def delete_student(manager):
    print("\n--- Delete Student ---")
    student = ask_existing_student(manager)
    if student is None:
        return
    if ask_yes_no(f"Are you sure you want to delete {student.name} ({student.student_id})?"):
        manager.delete_student(student.student_id)
        print("Student deleted and change saved.")
    else:
        print("Deletion cancelled.")


def filter_by_department(manager):
    department = ask("Department: ", validate_department)
    print(students_table(manager.filter_by_department(department)))


def filter_by_grade(manager):
    grade = ask("Grade (A+, A, B, C, D, F): ", validate_grade)
    print(students_table(manager.filter_by_grade(grade)))


def sort_students(manager):
    choice = input("Sort by 1) Name  2) Average marks (highest first): ").strip()
    if choice == "1":
        print(students_table(manager.sort_by_name()))
    elif choice == "2":
        print(students_table(manager.sort_by_average()))
    else:
        print("Invalid choice.")


def show_top_students(manager):
    print("\n--- Top 3 Students ---")
    print(students_table(manager.top_students(3)))


def show_highest_and_lowest(manager):
    for label, student in (("Highest", manager.highest_student()),
                           ("Lowest", manager.lowest_student())):
        if student is None:
            print("No students registered yet.")
            return
        print(f"{label}-scoring student: {student.name} ({student.student_id}) - "
              f"{student.percentage:.2f}%  Grade {student.grade}")


def show_passed(manager):
    print("\n--- Students Who Passed ---")
    print(students_table(manager.passed_students()))


def show_failed(manager):
    print("\n--- Students Who Failed ---")
    print(students_table(manager.failed_students()))


def show_student_report(manager):
    student = ask_existing_student(manager)
    if student:
        print(student_report(student))


def show_statistics(manager):
    print(format_statistics(class_statistics(manager)))


# (menu number, label, function) - the menu and the action lookup are built from this list
MENU_ITEMS = [
    ("1", "Add student", add_student),
    ("2", "Display all students", show_all_students),
    ("3", "Search student (ID / name)", search_student),
    ("4", "Update student", update_student),
    ("5", "Delete student", delete_student),
    ("6", "Filter by department", filter_by_department),
    ("7", "Filter by grade", filter_by_grade),
    ("8", "Sort students", sort_students),
    ("9", "Top 3 students", show_top_students),
    ("10", "Highest / lowest student", show_highest_and_lowest),
    ("11", "Students who passed", show_passed),
    ("12", "Students who failed", show_failed),
    ("13", "Individual result report", show_student_report),
    ("14", "Class statistics", show_statistics),
]
ACTIONS = {number: action for number, _, action in MENU_ITEMS}


def show_menu():
    print("\n" + "=" * 66)
    print("            STUDENT MANAGEMENT SYSTEM")
    print("=" * 66)
    half = (len(MENU_ITEMS) + 1) // 2  # print the menu in two columns
    for row in range(half):
        number, label, _ = MENU_ITEMS[row]
        line = f"{number:>3}. {label:<30}"
        if row + half < len(MENU_ITEMS):
            number, label, _ = MENU_ITEMS[row + half]
            line += f"{number:>3}. {label}"
        print(line)
    print("  0. Exit")


def main():
    file_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_DATA_FILE
    manager = StudentManager(file_path)
    for warning in manager.warnings:
        print(f"Warning: {warning}")
    print(f"Loaded {len(manager.students)} student(s) from {os.path.basename(file_path)}")

    try:
        while True:
            show_menu()
            choice = input("Choose an option: ").strip()
            if choice == "0":
                break
            action = ACTIONS.get(choice)
            if action is None:
                print("Invalid option. Please choose a number from the menu.")
                continue
            try:
                action(manager)
            except (ValueError, OSError) as error:  # keep the program running
                print(f"Error: {error}")
    except (KeyboardInterrupt, EOFError):
        print()  # Ctrl+C / Ctrl+D ends the program cleanly
    print("Goodbye! All changes were saved.")


if __name__ == "__main__":
    main()
