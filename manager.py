"""StudentManager: all operations on the collection of students.

Every method that changes data saves the JSON file straight away.
"""

from storage import load_students, save_students
from validators import validate_id


class StudentManager:
    def __init__(self, file_path):
        self.file_path = file_path
        self.students, self.warnings = load_students(file_path)

    def _save(self):
        save_students(self.file_path, self.students)

    # ---------- add / update / delete ----------
    def add_student(self, student):
        if self.find_by_id(student.student_id):
            raise ValueError(f"Student ID {student.student_id} already exists.")
        self.students.append(student)
        self._save()

    def update_student(self, student_id, field, value):
        student = self._get_or_fail(student_id)
        student.update_field(field, value)
        self._save()

    def update_mark(self, student_id, subject, mark):
        student = self._get_or_fail(student_id)
        student.update_mark(subject, mark)
        self._save()

    def delete_student(self, student_id):
        student = self._get_or_fail(student_id)
        self.students.remove(student)
        self._save()

    def _get_or_fail(self, student_id):
        student = self.find_by_id(student_id)
        if student is None:
            raise ValueError(f"No student found with ID {str(student_id).strip().upper()}.")
        return student

    # ---------- searching ----------
    def find_by_id(self, student_id):
        """Return the student with this ID (case-insensitive) or None."""
        try:
            student_id = validate_id(student_id)
        except ValueError:
            return None
        for student in self.students:
            if student.student_id == student_id:
                return student
        return None

    def search_by_name(self, text):
        """Case-insensitive search; matches any part of the full name."""
        text = text.strip().lower()
        if not text:
            return []
        return [s for s in self.students if text in s.name.lower()]

    # ---------- filtering ----------
    def filter_by_department(self, department):
        department = department.strip().lower()
        return [s for s in self.students if s.department.lower() == department]

    def filter_by_grade(self, grade):
        grade = grade.strip().upper()
        return [s for s in self.students if s.grade == grade]

    def passed_students(self):
        return [s for s in self.students if s.passed]

    def failed_students(self):
        return [s for s in self.students if not s.passed]

    # ---------- sorting and ranking ----------
    def sort_by_name(self):
        return sorted(self.students, key=lambda s: s.name.lower())

    def sort_by_average(self):
        """Highest average first."""
        return sorted(self.students, key=lambda s: s.percentage, reverse=True)

    def top_students(self, count=3):
        return self.sort_by_average()[:count]

    def highest_student(self):
        return max(self.students, key=lambda s: s.percentage, default=None)

    def lowest_student(self):
        return min(self.students, key=lambda s: s.percentage, default=None)
