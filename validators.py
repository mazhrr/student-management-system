"""Input validation helpers.

Every validate_* function takes a raw value, returns the cleaned value and
raises ValueError with a friendly message when the value is not acceptable.
The same functions are used by the command-line menus and when loading the
JSON file, so bad data is rejected in both places.
"""

import re

from academics import GRADES, MAX_MARK

MIN_SUBJECTS = 5


def validate_id(value):
    """Student ID: 3-10 letters or digits, stored in upper case."""
    value = str(value).strip().upper()
    if not re.fullmatch(r"[A-Z0-9]{3,10}", value):
        raise ValueError("ID must be 3-10 letters or digits (example: S001).")
    return value


def validate_name(value):
    """Full name: letters, spaces, dots, apostrophes and hyphens only."""
    value = " ".join(str(value).split())  # remove extra spaces
    if not re.fullmatch(r"[A-Za-z][A-Za-z .'-]+", value):
        raise ValueError("Name must contain only letters and spaces (at least 2 characters).")
    return value.title()


def validate_age(value):
    """Age: a whole number between 5 and 100."""
    try:
        age = int(str(value).strip())
    except ValueError:
        raise ValueError("Age must be a whole number.")
    if not 5 <= age <= 100:
        raise ValueError("Age must be between 5 and 100.")
    return age


def validate_email(value):
    """Email: simple check for name@domain.ext."""
    value = str(value).strip().lower()
    if not re.fullmatch(r"[\w.+-]+@[\w-]+(\.[\w-]+)+", value):
        raise ValueError("Enter a valid email (example: name@example.com).")
    return value


def validate_department(value):
    """Department: letters and spaces only."""
    value = " ".join(str(value).split())
    if not re.fullmatch(r"[A-Za-z][A-Za-z ]+", value):
        raise ValueError("Department must contain only letters and spaces.")
    return value.title()


def validate_subject(value):
    """Subject name: letters, digits and spaces."""
    value = " ".join(str(value).split())
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9 ]*", value):
        raise ValueError("Subject name must start with a letter (letters, digits, spaces only).")
    return value.title()


def validate_mark(value):
    """A single subject mark: a number from 0 to MAX_MARK."""
    try:
        mark = float(str(value).strip())
    except ValueError:
        raise ValueError("Marks must be a number.")
    if not 0 <= mark <= MAX_MARK:  # also rejects NaN
        raise ValueError(f"Marks must be between 0 and {MAX_MARK}.")
    return mark


def validate_marks(marks):
    """A dictionary of {subject: mark} with at least MIN_SUBJECTS subjects."""
    if not isinstance(marks, dict):
        raise ValueError("Marks must be a dictionary of subject: mark.")
    cleaned = {}
    for subject, mark in marks.items():
        cleaned[validate_subject(subject)] = validate_mark(mark)
    if len(cleaned) < MIN_SUBJECTS:
        raise ValueError(f"At least {MIN_SUBJECTS} different subjects are required.")
    return cleaned


def validate_grade(value):
    """Grade letter used for filtering: one of A+, A, B, C, D, F."""
    value = str(value).strip().upper()
    if value not in GRADES:
        raise ValueError("Grade must be one of: " + ", ".join(GRADES))
    return value
