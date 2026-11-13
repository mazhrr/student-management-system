"""Text reports: student table, individual result report and class statistics.

These functions only build strings / dictionaries; printing is done in main.py.
"""

from collections import Counter

from academics import GRADES, MAX_MARK


def students_table(students):
    """One row per student."""
    if not students:
        return "No students found."
    header = (f"{'ID':<8}{'Name':<22}{'Age':<5}{'Email':<30}{'Department':<18}"
              f"{'Avg %':>7}  {'Grade':<6}{'Status'}")
    lines = [header, "-" * len(header)]
    for s in students:
        lines.append(f"{s.student_id:<8}{s.name:<22}{s.age:<5}{s.email:<30}{s.department:<18}"
                     f"{s.percentage:>7.2f}  {s.grade:<6}{s.status}")
    return "\n".join(lines)


def student_report(student):
    """Detailed result report for one student."""
    line = "=" * 44
    lines = [
        line,
        "          STUDENT RESULT REPORT",
        line,
        f"ID          : {student.student_id}",
        f"Name        : {student.name}",
        f"Age         : {student.age}",
        f"Email       : {student.email}",
        f"Department  : {student.department}",
        "-" * 44,
        f"{'Subject':<28}{'Marks':>8}",
    ]
    for subject, mark in student.marks.items():
        lines.append(f"{subject:<28}{mark:>8g}")
    lines += [
        "-" * 44,
        f"Total marks : {student.total:g} / {len(student.marks) * MAX_MARK}",
        f"Percentage  : {student.percentage:.2f}%",
        f"Grade       : {student.grade}",
        f"Result      : {student.status.upper()}",
        line,
    ]
    return "\n".join(lines)


def class_statistics(manager):
    """Return a dictionary of class-wide numbers (None if there are no students)."""
    students = manager.students
    if not students:
        return None
    grade_counts = Counter(s.grade for s in students)
    return {
        "total": len(students),
        "passed": len(manager.passed_students()),
        "failed": len(manager.failed_students()),
        "class_average": round(sum(s.percentage for s in students) / len(students), 2),
        "highest": manager.highest_student(),
        "lowest": manager.lowest_student(),
        "grade_counts": {grade: grade_counts[grade] for grade in GRADES},
        "department_counts": dict(sorted(Counter(s.department for s in students).items())),
    }


def format_statistics(stats):
    """Turn the dictionary from class_statistics into printable text."""
    if stats is None:
        return "No students registered yet."
    highest, lowest = stats["highest"], stats["lowest"]
    lines = [
        "=" * 44,
        "             CLASS STATISTICS",
        "=" * 44,
        f"Total registered students : {stats['total']}",
        f"Total passed              : {stats['passed']}",
        f"Total failed              : {stats['failed']}",
        f"Overall class average     : {stats['class_average']:.2f}%",
        f"Highest student average   : {highest.percentage:.2f}%  ({highest.name})",
        f"Lowest student average    : {lowest.percentage:.2f}%  ({lowest.name})",
        "-" * 44,
        "Students in each grade:",
    ]
    for grade, count in stats["grade_counts"].items():
        lines.append(f"  Grade {grade:<3}: {count}")
    lines += ["-" * 44, "Students per department:"]
    for department, count in stats["department_counts"].items():
        lines.append(f"  {department:<20}: {count}")
    lines.append("=" * 44)
    return "\n".join(lines)
