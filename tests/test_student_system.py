"""Test cases for the Student Management System.

Run from the project folder with:   python -m unittest discover -s tests -v
Every test uses a temporary folder, so the real data file is never touched.
"""

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from academics import get_grade, is_pass  # noqa: E402
from manager import StudentManager  # noqa: E402
from reports import class_statistics  # noqa: E402
from student import Student  # noqa: E402
from validators import validate_age, validate_email, validate_mark, validate_name  # noqa: E402

SUBJECTS = ["Math", "English", "Physics", "Chemistry", "Computer Science"]


def make_student(student_id="S001", name="Asad Khan", mark=80, department="Computer Science"):
    """Build a valid student whose five subject marks are all equal to `mark`."""
    marks = {subject: mark for subject in SUBJECTS}
    return Student(student_id, name, 20, "test@example.com", department, marks)


class StudentSystemTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.file_path = os.path.join(self.temp_dir.name, "students.json")
        self.manager = StudentManager(self.file_path)

    def tearDown(self):
        self.temp_dir.cleanup()

 
    # ---------------- normal cases ----------------
    def test_01_total_percentage_and_grade(self):
        student = Student("S010", "Test User", 20, "t@example.com", "Physics",
                          {"A": 90, "B": 80, "C": 70, "D": 60, "E": 50})
        self.assertEqual(student.total, 350)
        self.assertEqual(student.percentage, 70.0)
        self.assertEqual(student.grade, "B")

    def test_02_grade_boundaries_and_pass_fail(self):
        self.assertEqual(get_grade(90), "A+")
        self.assertEqual(get_grade(89.99), "A")
        self.assertEqual(get_grade(40), "D")
        self.assertEqual(get_grade(39.99), "F")
        self.assertTrue(is_pass(40))
        self.assertFalse(is_pass(39.99))

    def test_03_add_student_is_saved_to_json(self):
        self.manager.add_student(make_student())
        with open(self.file_path, encoding="utf-8") as file:
            saved = json.load(file)
        self.assertEqual(len(saved), 1)
        self.assertEqual(saved[0]["student_id"], "S001")
        # a new manager (a "restart" of the app) loads the same data back
        self.assertEqual(len(StudentManager(self.file_path).students), 1)

    def test_04_search_by_id_and_name_case_insensitive(self):
        self.add_three_students()
        self.assertEqual(self.manager.find_by_id("s002").name, "Bilal Hussain")
        self.assertEqual(len(self.manager.search_by_name("Asad")), 1)
        self.assertEqual([s.name for s in self.manager.search_by_name("ali")], [" Ali"])
        self.assertIsNone(self.manager.find_by_id("S999"))

    def test_05_update_student_and_persist(self):
        self.manager.add_student(make_student())
        self.manager.update_student("S001", "age", "25")
        self.manager.update_mark("S001", "math", 100)
        reloaded = StudentManager(self.file_path).find_by_id("S001")
        self.assertEqual(reloaded.age, 25)
        self.assertEqual(reloaded.marks["Math"], 100)

    def test_06_delete_student_and_persist(self):
        self.add_three_students()
        self.manager.delete_student("S002")
        self.assertIsNone(self.manager.find_by_id("S002"))
        self.assertEqual(len(StudentManager(self.file_path).students), 2)

    def test_07_sorting_and_top_students(self):
        self.add_three_students()
        self.assertEqual([s.name for s in self.manager.sort_by_name()],
                         ["Asad Khan", "Bilal Hussain", " Ali"])
        self.assertEqual([s.student_id for s in self.manager.sort_by_average()],
                         ["S001", "S002", "S003"])
        self.manager.add_student(make_student("S004", "Dina Shah", 70))
        self.assertEqual([s.student_id for s in self.manager.top_students(3)],
                         ["S001", "S004", "S002"])

    def test_08_filter_by_department_grade_and_pass_fail(self):
        self.add_three_students()
        self.assertEqual(len(self.manager.filter_by_department("physics")), 2)
        self.assertEqual([s.student_id for s in self.manager.filter_by_grade("a+")], ["S001"])
        self.assertEqual(len(self.manager.passed_students()), 2)
        self.assertEqual([s.student_id for s in self.manager.failed_students()], ["S003"])
        self.assertEqual(self.manager.highest_student().student_id, "S001")
        self.assertEqual(self.manager.lowest_student().student_id, "S003")

    def test_09_class_statistics(self):
        self.add_three_students()
        stats = class_statistics(self.manager)
        self.assertEqual(stats["total"], 3)
        self.assertEqual(stats["passed"], 2)
        self.assertEqual(stats["failed"], 1)
        self.assertEqual(stats["class_average"], 53.33)
        self.assertEqual(stats["grade_counts"]["A+"], 1)
        self.assertEqual(stats["grade_counts"]["F"], 1)
        self.assertEqual(stats["department_counts"], {"Computer Science": 1, "Physics": 2})

    # ---------------- invalid input cases ----------------
    def test_10_duplicate_id_is_rejected(self):
        self.manager.add_student(make_student("S001"))
        with self.assertRaises(ValueError):
            self.manager.add_student(make_student("s001", "Another Person"))
        self.assertEqual(len(self.manager.students), 1)

    def test_11_invalid_names_are_rejected(self):
        for bad_name in ["", "   ", "A", "John123", "@#$%"]:
            with self.assertRaises(ValueError, msg=bad_name):
                validate_name(bad_name)
        self.assertEqual(validate_name("  ali   raza "), "Ali Raza")

    def test_12_invalid_age_is_rejected(self):
        for bad_age in ["abc", "", "-5", "3", "150", "20.5"]:
            with self.assertRaises(ValueError, msg=bad_age):
                validate_age(bad_age)
        self.assertEqual(validate_age(" 21 "), 21)

    def test_13_invalid_email_is_rejected(self):
        for bad_email in ["", "plainaddress", "a@b", "@example.com", "a b@example.com"]:
            with self.assertRaises(ValueError, msg=bad_email):
                validate_email(bad_email)
        self.assertEqual(validate_email("User@Example.COM"), "user@example.com")

    def test_14_invalid_marks_are_rejected(self):
        for bad_mark in ["abc", "", "-1", "101", "nan"]:
            with self.assertRaises(ValueError, msg=bad_mark):
                validate_mark(bad_mark)
        self.assertEqual(validate_mark("0"), 0)
        self.assertEqual(validate_mark("100"), 100)

    def test_15_fewer_than_five_subjects_is_rejected(self):
        with self.assertRaises(ValueError):
            Student("S001", "Test User", 20, "t@example.com", "Physics",
                    {"Math": 50, "English": 60, "Physics": 70, "Chemistry": 80})

    def test_16_update_with_invalid_value_keeps_old_value(self):
        self.manager.add_student(make_student())
        with self.assertRaises(ValueError):
            self.manager.update_student("S001", "age", "abc")
        with self.assertRaises(ValueError):
            self.manager.update_student("S001", "id", "S999")  # ID cannot be changed
        self.assertEqual(self.manager.find_by_id("S001").age, 20)

    def test_17_update_or_delete_missing_student_gives_error(self):
        with self.assertRaises(ValueError):
            self.manager.update_student("S404", "age", "30")
        with self.assertRaises(ValueError):
            self.manager.delete_student("S404")

    # ---------------- data file problems ----------------
    def test_18_missing_file_starts_empty(self):
        self.assertEqual(self.manager.students, [])
        self.assertTrue(self.manager.warnings)  # a warning explains what happened

    def test_19_corrupted_file_does_not_crash(self):
        with open(self.file_path, "w", encoding="utf-8") as file:
            file.write("{ this is not valid json ")
        manager = StudentManager(self.file_path)
        self.assertEqual(manager.students, [])
        self.assertTrue(manager.warnings)
        self.assertTrue(os.path.exists(self.file_path + ".corrupted"))  # bad file kept as backup
        manager.add_student(make_student())  # and the app can keep working
        self.assertEqual(len(StudentManager(self.file_path).students), 1)

    def test_20_invalid_and_duplicate_records_are_skipped(self):
        good = make_student().to_dict()
        records = [
            good,
            {**good, "student_id": "S002", "age": "abc"},   # invalid age
            {"student_id": "S003"},                          # missing fields
            "not a record",                                  # wrong type
            dict(good),                                      # duplicate ID
        ]
        with open(self.file_path, "w", encoding="utf-8") as file:
            json.dump(records, file)
        manager = StudentManager(self.file_path)
        self.assertEqual(len(manager.students), 1)
        self.assertEqual(len(manager.warnings), 4)


if __name__ == "__main__":
    unittest.main()
