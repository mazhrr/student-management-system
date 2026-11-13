"""Academic rules: maximum marks, pass mark and grade table.

Keeping the rules in one place means a rule change (for example the pass
percentage) only has to be made here.
"""

MAX_MARK = 100          # maximum marks for every subject
PASS_PERCENTAGE = 40    # minimum average percentage needed to pass

# (minimum percentage, grade) - checked from the top down
GRADE_TABLE = [
    (90, "A+"),
    (80, "A"),
    (70, "B"),
    (60, "C"),
    (40, "D"),
]
GRADES = ["A+", "A", "B", "C", "D", "F"]  # F is anything below 40


def get_grade(percentage):
    """Return the letter grade for a percentage."""
    for minimum, grade in GRADE_TABLE:
        if percentage >= minimum:
            return grade
    return "F"


def is_pass(percentage):
    """Return True if the percentage is enough to pass."""
    return percentage >= PASS_PERCENTAGE
