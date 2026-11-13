# Advanced Student Management System

A command-line Student Management System written in plain Python 3 (standard library only).
It manages student records, calculates results, produces reports and saves everything permanently in a JSON file.

## Requirements

- Python 3.8 or newer
- Nothing to install: no external packages, frameworks or databases

## How to run

```bash
cd student_management
python main.py          # on some systems: python3 main.py
```

The app loads `data/students.json` (8 sample students are included) and shows a menu.
Type the number of an option and press Enter. Every change is saved automatically.

To use a different data file: `python main.py path/to/other_file.json`

## How to run the tests

```bash
python -m unittest discover -s tests -v


20 test cases run against a temporary folder, so your real data file is never touched.

## Project structure


student_management/
├── main.py            # command-line menu (the only file that uses input/print for menus)
├── manager.py         # StudentManager: add, update, delete, search, filter, sort, rank
├── student.py         # Student class: data + total / percentage / grade / pass-fail
├── validators.py      # validation functions for every input
├── academics.py       # grade table, pass percentage, max marks (rules in one place)
├── storage.py         # load/save JSON, handles missing or corrupted files
├── reports.py         # student table, individual report, class statistics
├── data/
│   └── students.json  # sample student records (created/updated automatically)
├── tests/
│   └── test_student_system.py   # 20 test cases
├── screenshots/       # recorded sessions of every feature (.png and .txt)
└── README.md
```

## Menu options

| #   | Option                   | What it does                                                                                                                                                        |
| --- | ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Add student              | Asks for ID, name, age, email, department and 5 subject marks (more subjects optional). Every answer is validated and re-asked if wrong. Duplicate IDs are refused. |
| 2   | Display all students     | Table of every student with average, grade and pass/fail.                                                                                                           |
| 3   | Search student           | By ID, or by name (case-insensitive, partial names work).                                                                                                           |
| 4   | Update student           | Change name, age, email, department or one subject mark.                                                                                                            |
| 5   | Delete student           | Asks for confirmation first.                                                                                                                                        |
| 6   | Filter by department     | Case-insensitive.                                                                                                                                                   |
| 7   | Filter by grade          | A+, A, B, C, D or F.                                                                                                                                                |
| 8   | Sort students            | By name (A-Z) or by average marks (highest first).                                                                                                                  |
| 9   | Top 3 students           | Highest averages.                                                                                                                                                   |
| 10  | Highest / lowest student | Best and weakest average.                                                                                                                                           |
| 11  | Students who passed      |                                                                                                                                                                     |
| 12  | Students who failed      |                                                                                                                                                                     |
| 13  | Individual result report | Subject marks, total, percentage, grade, result.                                                                                                                    |
| 14  | Class statistics         | Totals, passed/failed, class average, highest/lowest average, students per grade, students per department.                                                          |

## Rules used

| Item               | Rule                                               |
| ------------------ | -------------------------------------------------- |
| Each subject       | Marked out of 100, at least 5 subjects per student |
| Total              | Sum of all subject marks                           |
| Average percentage | total ÷ (number of subjects × 100) × 100           |
| Grade              | A+ ≥ 90, A ≥ 80, B ≥ 70, C ≥ 60, D ≥ 40, F < 40    |
| Pass / Fail        | Pass if average percentage ≥ 40                    |

To change these rules, edit only `academics.py`.

Input rules (`validators.py`): ID = 3-10 letters/digits (stored in upper case, must be unique);
name = letters and spaces, 2+ characters; age = whole number 5-100; email = `name@domain.ext`;
department = letters and spaces; marks = number 0-100. The ID cannot be changed after creation, so IDs always stay unique.

## Data file format

`data/students.json` is a list of students:

```json
{
  "student_id": "S001",
  "name": "Asad",
  "age": 20,
  "email": "asad.khan@example.com",
  "department": "Computer Science",
  "marks": {
    "Math": 92.0,
    "English": 88.0,
    "Physics": 95.0,
    "Chemistry": 90.0,
    "Computer Science": 85.0
  }
}
```

Total, percentage, grade and status are **calculated** from the marks and never stored, so they can never get out of date.

### What happens when the file has problems

| Problem                           | Behaviour                                                                                    |
| --------------------------------- | -------------------------------------------------------------------------------------------- |
| File missing                      | Starts with an empty list; the file is created on the first save.                            |
| File corrupted / not valid JSON   | The bad file is kept as `students.json.corrupted`, the app starts empty and shows a warning. |
| A record is invalid or incomplete | That record is skipped with a warning; good records still load.                              |
| Duplicate ID in the file          | The second one is skipped with a warning.                                                    |
| Typing mistakes in the menu       | Re-asked; the program never stops on bad input.                                              |
| Ctrl+C / Ctrl+D                   | Exits cleanly (data is already saved).                                                       |

Saving writes to a temporary file first and then replaces the real file, so a crash during saving cannot damage existing data.

## How the code works (for explaining the project)

1. **`main.py`** builds the menu from the `MENU_ITEMS` list and calls one small function per option. The helper `ask(prompt, validator)` keeps asking until the validator accepts the input, so validation is written once and reused for every field.
2. **`manager.py`** holds the list of students. `add_student`, `update_student`, `update_mark` and `delete_student` call `_save()` right after changing the list. Search, filter and sort use list comprehensions and `sorted(..., key=...)`.
3. **`student.py`** – a `Student` validates every value in `__init__`, so an invalid student object can never exist. Results are `@property` methods calculated from `marks`. `to_dict()` / `from_dict()` convert to and from JSON.
4. **`validators.py`** – each function cleans the value and raises `ValueError` with a clear message. The same functions are used when typing and when loading the file.
5. **`storage.py`** – `load_students` returns `(students, warnings)`; it catches file and JSON errors and skips bad records instead of crashing.
6. **`reports.py`** – builds the text tables/reports; `class_statistics` uses `collections.Counter` for the grade and department counts.
7. **`academics.py`** – grade table and pass mark, so rules are not scattered through the code.

Concepts demonstrated: functions, classes/OOP (`Student`, `StudentManager`), properties, dictionaries, lists, list comprehensions, lambda sort keys, `Counter`, exception handling, file handling with JSON, modules and imports, regular expressions, unit testing.

## Test cases (20)

| #   | Test                                                              | Type          |
| --- | ----------------------------------------------------------------- | ------------- |
| 1   | Total, percentage and grade are calculated correctly              | Normal        |
| 2   | Grade boundaries (90, 89.99, 40, 39.99) and pass/fail             | Normal / edge |
| 3   | Adding a student saves to JSON and survives a restart             | Normal        |
| 4   | Search by ID (any case) and by name (case-insensitive)            | Normal        |
| 5   | Update student and subject mark, change persists                  | Normal        |
| 6   | Delete student, change persists                                   | Normal        |
| 7   | Sort by name, sort by average, top 3                              | Normal        |
| 8   | Filter by department / grade, passed, failed, highest, lowest     | Normal        |
| 9   | Class statistics (counts, average, grades, departments)           | Normal        |
| 10  | Duplicate student ID is rejected                                  | Invalid       |
| 11  | Invalid names (empty, 1 letter, digits, symbols)                  | Invalid       |
| 12  | Invalid ages (text, empty, negative, too small/large, decimal)    | Invalid       |
| 13  | Invalid emails                                                    | Invalid       |
| 14  | Invalid marks (text, empty, negative, over 100, NaN)              | Invalid       |
| 15  | Fewer than 5 subjects is rejected                                 | Invalid       |
| 16  | Invalid update keeps the old value; ID cannot be changed          | Invalid       |
| 17  | Updating / deleting a student that does not exist                 | Invalid       |
| 18  | Missing data file starts empty                                    | File problem  |
| 19  | Corrupted data file does not crash and the app keeps working      | File problem  |
| 20  | Invalid, incomplete and duplicate records in the file are skipped | File problem  |

Result: `Ran 20 tests ... OK` (see `screenshots/13_test_results.png`).

## Screenshots

All screenshots are real recorded sessions of the program (typed input is shown in green).
A `.txt` copy of each is next to the `.png`. They were recorded on a copy of the sample data, one session after another,
so you can see changes (added/updated/deleted students) survive between sessions.

| File                             | Shows                                                                        |
| -------------------------------- | ---------------------------------------------------------------------------- |
| `01_menu_and_display_all`        | Main menu and the list of all students                                       |
| `02_add_student_with_validation` | Adding a student; invalid name/age/email/marks and duplicate ID are rejected |
| `03_search_by_id_and_name`       | Search by ID, by name (case-insensitive), and no result                      |
| `04_update_student`              | Updating age and a subject mark, unknown ID, then the updated report         |
| `05_delete_with_confirmation`    | Delete cancelled, invalid answer, delete confirmed                           |
| `06_filter_sort_top3`            | Filter by department and grade, sort by name and average, top 3              |
| `07_academic_results`            | Highest/lowest student, passed, failed, individual report                    |
| `08_class_statistics`            | Class statistics report                                                      |
| `09_invalid_menu_and_missing_id` | Invalid menu choices and unknown ID                                          |
| `10_corrupted_data_file`         | Corrupted JSON file handled                                                  |
| `11_invalid_records_skipped`     | Bad records in the file skipped with warnings                                |
| `12_missing_data_file`           | Missing file handled, file created on first add                              |
| `13_test_results`                | All 20 tests passing                                                         |

## Possible extensions

- Let the user choose subjects per department.
- Export a result report to a text or CSV file.
- Add a login (admin / teacher) before the menu.
- Add a per-subject statistics report.
