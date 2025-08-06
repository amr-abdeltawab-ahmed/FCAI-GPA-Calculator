# FCAI GPA Calculator

![Python](https://img.shields.io/badge/python-3.7%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

A comprehensive GPA calculator for students of the Faculty of Computer Science and Artificial Intelligence (FCAI) at Cairo University, with official bylaw support and customizable grading systems.

## Features

- **Official Bylaw Compliance**: Calculates GPA exactly according to FCAI regulations
- **Automatic Data Retrieval**: Logs into the FCAI system to fetch your courses and grades
- **Customizable Grading**: Modify grade points and thresholds via `Bylaw.json`
- **Detailed Reporting**: Shows GPA, total points, hours, and general grade
- **Data Export**: Saves your course information to JSON for offline analysis

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/FCAI-GPA-Calculator.git
   cd FCAI-GPA-Calculator
   ```
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the main script:
   ```bash
   python main.py
   ```
2. Enter your student ID and password when prompted. The script will:
   - Log in to the FCAI system
   - Fetch your courses and grades
   - Calculate your GPA and general grade
   - Save your course data to `fcai_courses.json`
   - Display a summary of your GPA calculation in the terminal

### Example Output
```
Enter your student ID: 2020xxxxxx
Enter your password: ********
Successfully saved courses data to fcai_courses.json

GPA Calculation Results:
Total Points: 123.4
Total Hours: 40
GPA: 3.09
General Grade: جيد جدا
Number of Courses Counted: 15
```

## Customizing the Grading System

The grading system and general grade thresholds are defined in `Bylaw.json`. You can edit this file to match any changes in the official bylaw or your own requirements. Example structure:
```json
{
    "grade_points": {
        "A+": 4.0,
        "A": 3.7,
        "B+": 3.3,
        "B": 3.0,
        "C+": 2.7,
        "C": 2.4,
        "D+": 2.2,
        "D": 2.0,
        "F": 0.0
    },
    "gpa_general_grade": [
        {"threshold": 3.5, "grade": "ممتاز"},
        {"threshold": 3.0, "grade": "جيد جدا"},
        {"threshold": 2.5, "grade": "جيد"},
        {"threshold": 2.0, "grade": "مقبول"},
        {"threshold": 1.5, "grade": "ضعيف"},
        {"threshold": 0.0, "grade": "ضعيف جدا"}
    ]
}
```
If `Bylaw.json` does not exist, the program will create it with default values.

## Notes
- Your credentials are only used to fetch your data from the FCAI system and are not stored.
- The script requires an internet connection to access the FCAI API.
- For any issues or feature requests, please open an issue on the repository.

## License

This project is licensed under the MIT License.

