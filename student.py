"""The Student class: holds one student's data and calculates their results."""

from academics import MAX_MARK, get_grade, is_pass
from validators import (
    validate_age,
    validate_department,
    validate_email,
    validate_id,
    validate_mark,
    validate_marks,
    validate_name,
    validate_subject,
)

# Fields that can be changed after a student is created (the ID is fixed
# so that IDs always stay unique).
FIELD_VALIDATORS = {
    "name": validate_name,
    "age": validate_age,
    "email": validate_email,
    "department": validate_department,
}


class Student:
    def __init__(self, student_id, name, age, email, department, marks):
        # Every value is validated here, so a Student object is always valid.
        self.student_id = validate_id(student_id)
        self.name = validate_name(name)
        self.age = validate_age(age)
        self.email = validate_email(email)
        self.department = validate_department(department)
        self.marks = validate_marks(marks)  # {subject: mark}

    # ---------- academic results (calculated, never stored) ----------
    @property
    def total(self):
        return sum(self.marks.values())

    @property
    def percentage(self):
        return round(self.total / (len(self.marks) * MAX_MARK) * 100, 2)

    @property
    def grade(self):
        return get_grade(self.percentage)

    @property
    def passed(self):
        return is_pass(self.percentage)

    @property
    def status(self):
        return "Pass" if self.passed else "Fail"

    # ---------- updating ----------
    def update_field(self, field, value):
        """Change name, age, email or department (value is validated first)."""
        if field not in FIELD_VALIDATORS:
            raise ValueError(f"'{field}' cannot be updated.")
        setattr(self, field, FIELD_VALIDATORS[field](value))

    def update_mark(self, subject, mark):
        """Change the mark of a subject the student already has."""
        subject = validate_subject(subject)
        if subject not in self.marks:
            raise ValueError(f"'{subject}' is not one of this student's subjects.")
        self.marks[subject] = validate_mark(mark)

    # ---------- converting to and from JSON-friendly dictionaries ----------
    def to_dict(self):
        return {
            "student_id": self.student_id,
            "name": self.name,
            "age": self.age,
            "email": self.email,
            "department": self.department,
            "marks": self.marks,
        }

    @classmethod
    def from_dict(cls, data):
        if not isinstance(data, dict):
            raise ValueError("record is not an object")
        try:
            return cls(
                data["student_id"], data["name"], data["age"],
                data["email"], data["department"], data["marks"],
            )
        except KeyError as error:
            raise ValueError(f"missing field {error}")
