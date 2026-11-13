"""Reading and writing the JSON data file.

load_students never crashes: a missing file gives an empty list, a corrupted
file is moved aside, and invalid or duplicate records are skipped. Everything
that went wrong is returned as a list of warning messages.
"""

import json
import os

from student import Student


def load_students(file_path):
    """Return (list_of_students, list_of_warnings)."""
    warnings = []

    if not os.path.exists(file_path):
        warnings.append("Data file not found. Starting with an empty student list.")
        return [], warnings

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            records = json.load(file)
        if not isinstance(records, list):
            raise ValueError("expected a list of students")
    except (ValueError, OSError):  # JSONDecodeError and UnicodeDecodeError are ValueErrors
        backup_path = file_path + ".corrupted"
        try:
            os.replace(file_path, backup_path)
            warnings.append(
                f"Data file is corrupted. It was kept as '{os.path.basename(backup_path)}' "
                "and a new empty list was started."
            )
        except OSError:
            warnings.append("Data file could not be read. Starting with an empty student list.")
        return [], warnings

    students = []
    seen_ids = set()
    for number, record in enumerate(records, start=1):
        try:
            student = Student.from_dict(record)
        except ValueError as error:
            warnings.append(f"Skipped record #{number}: {str(error).rstrip('.')}.")
            continue
        if student.student_id in seen_ids:
            warnings.append(f"Skipped record #{number}: duplicate ID {student.student_id}.")
            continue
        seen_ids.add(student.student_id)
        students.append(student)
    return students, warnings


def save_students(file_path, students):
    """Write all students to the JSON file (via a temp file for safety)."""
    folder = os.path.dirname(file_path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    temp_path = file_path + ".tmp"
    with open(temp_path, "w", encoding="utf-8") as file:
        json.dump([student.to_dict() for student in students], file, indent=4)
    os.replace(temp_path, file_path)  # replace only after the write succeeded
