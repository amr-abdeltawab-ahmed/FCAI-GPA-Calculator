import requests
import json
import os
from typing import List, Dict


class FCAIGPACalculator:
    def __init__(self, username: str, password: str):
        self.base_url = "http://193.227.14.58/api"
        self.session = requests.Session()
        self.id_token = None
        self.username = username
        self.password = password
        self.student_id = username
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "Origin": "http://193.227.14.58",
            "Referer": "http://193.227.14.58/",
        }

        # Load grading system from Bylaw.json or use defaults
        self.grade_points, self.gpa_general_grade = self.load_bylaw()

    def load_bylaw(self) -> tuple:
        """Load grading system from Bylaw.json or use defaults"""
        default_grade_points = {
            "A+": 4.0,
            "A": 3.7,
            "B+": 3.3,
            "B": 3.0,
            "C+": 2.7,
            "C": 2.4,
            "D+": 2.2,
            "D": 2.0,
            "F": 0.0
        }

        default_gpa_general_grade = [
            {"threshold": 3.5, "grade": "ممتاز"},
            {"threshold": 3.0, "grade": "جيد جدا"},
            {"threshold": 2.5, "grade": "جيد"},
            {"threshold": 2.0, "grade": "مقبول"},
            {"threshold": 1.5, "grade": "ضعيف"},
            {"threshold": 0.0, "grade": "ضعيف جدا"}
        ]

        try:
            if os.path.exists("Bylaw.json"):
                with open("Bylaw.json", "r", encoding="utf-8") as f:
                    bylaw = json.load(f)

                # Convert list of dicts to list of tuples for gpa_general_grade
                gpa_general_grade = [
                    (item["threshold"], item["grade"])
                    for item in bylaw.get("gpa_general_grade", default_gpa_general_grade)
                ]

                return (
                    bylaw.get("grade_points", default_grade_points),
                    gpa_general_grade
                )
        except Exception as e:
            print(f"Error loading Bylaw.json, using defaults: {str(e)}")

        # Convert default list of dicts to list of tuples
        default_gpa_tuples = [
            (item["threshold"], item["grade"])
            for item in default_gpa_general_grade
        ]
        return default_grade_points, default_gpa_tuples

    def create_default_bylaw(self):
        """Create a default Bylaw.json file if it doesn't exist"""
        default_bylaw = {
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

        try:
            if not os.path.exists("Bylaw.json"):
                with open("Bylaw.json", "w", encoding="utf-8") as f:
                    json.dump(default_bylaw, f, ensure_ascii=False, indent=4)
                print("Created default Bylaw.json file")
        except Exception as e:
            print(f"Error creating default Bylaw.json: {str(e)}")

    def login(self) -> bool:
        """Authenticate with the FCAI system and get the JWT token"""
        login_url = f"{self.base_url}/authenticate"
        payload = {
            "username": self.username,
            "password": self.password,
            "rememberMe": False
        }

        try:
            response = self.session.post(
                login_url,
                headers=self.headers,
                data=json.dumps(payload))

            if response.status_code == 200:
                self.id_token = response.json().get("id_token")
                return True
            else:
                print(f"Login failed with status code: {response.status_code}")
                return False

        except Exception as e:
            print(f"Login error: {str(e)}")
            return False

    def get_courses_data(self) -> List[Dict]:
        """Retrieve all courses data for the student"""
        if not self.id_token:
            if not self.login():
                return []

        courses_url = f"{self.base_url}/student-courses?size=150&studentId.equals={self.student_id}&includeWithdraw.equals=true"

        try:
            headers = self.headers.copy()
            headers["Authorization"] = f"Bearer {self.id_token}"

            response = self.session.get(
                courses_url,
                headers=headers)

            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to get courses data with status code: {response.status_code}")
                return []

        except Exception as e:
            print(f"Error getting courses data: {str(e)}")
            return []

    def extract_courses_info(self, courses_data: List[Dict]) -> List[Dict]:
        """Extract relevant course information (name, code, hours, grade)"""
        extracted_courses = []

        for course in courses_data:
            try:
                course_info = {
                    "code": course["course"]["code"],
                    "name": course["course"]["name"],
                    "arabic_name": course["course"]["arabicName"],
                    "hours": course["course"]["numOfHours"],
                    "grade": course.get("grade"),
                    "result": course.get("result"),
                    "type": course["course"]["type"]["name"],
                    "level": course["level"]["name"],
                    "term": course["term"]["name"]
                }

                # Calculate points based on percentage if grade is not available
                if course_info["grade"] is None and course_info["result"] is not None:
                    course_info["grade"] = self._percentage_to_grade(float(course_info["result"]))

                extracted_courses.append(course_info)
            except KeyError as e:
                print(f"Missing key in course data: {str(e)}")
                continue

        return extracted_courses

    def _percentage_to_grade(self, percentage: float) -> str:
        """Convert percentage score to letter grade based on FCAI bylaw"""
        if percentage >= 90:
            return "A+"
        elif percentage >= 85:
            return "A"
        elif percentage >= 80:
            return "B+"
        elif percentage >= 75:
            return "B"
        elif percentage >= 70:
            return "C+"
        elif percentage >= 65:
            return "C"
        elif percentage >= 60:
            return "D+"
        elif percentage >= 50:
            return "D"
        else:
            return "F"

    def get_general_grade(self, gpa: float) -> str:
        """Determine general grade based on GPA according to FCAI bylaw"""
        for threshold, grade in self.gpa_general_grade:
            if gpa >= threshold:
                return grade
        return "ضعيف جدا"  # For GPAs below 0 (shouldn't happen)

    def save_courses_to_file(self, courses: List[Dict], filename: str = "fcai_courses.json"):
        """Save extracted courses data to a JSON file"""
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(courses, f, ensure_ascii=False, indent=4)
            print(f"Successfully saved courses data to {filename}")
        except Exception as e:
            print(f"Error saving courses to file: {str(e)}")

    def calculate_gpa(self, courses: List[Dict]) -> Dict:
        """
        Calculate GPA based on FCAI bylaw exactly
        Returns: {
            "total_points": float,
            "total_hours": int,
            "gpa": float,
            "courses_count": int,
            "general_grade": str
        }
        """
        total_points = 0.0
        total_hours = 0
        counted_courses = 0

        for course in courses:
            # Only count courses with valid grades
            if course.get("grade") and course.get("grade") in self.grade_points:
                try:
                    hours = int(course["hours"])
                    grade = course["grade"]
                    points = self.grade_points[grade]

                    total_points += points * hours
                    total_hours += hours
                    counted_courses += 1
                except (ValueError, KeyError) as e:
                    print(f"Error processing course {course.get('code')}: {str(e)}")
                    continue

        if total_hours > 0:
            gpa = total_points / total_hours
        else:
            gpa = 0.0

        # Determine general grade based on GPA
        general_grade = self.get_general_grade(gpa)

        return {
            "total_points": total_points,
            "total_hours": total_hours,
            "gpa": round(gpa, 2),
            "courses_count": counted_courses,
            "general_grade": general_grade
        }

    def run(self):
        """Run the full process: login, get data, calculate GPA"""
        if not self.login():
            print("Failed to login. Exiting.")
            return None

        courses_data = self.get_courses_data()
        if not courses_data:
            print("No courses data retrieved. Exiting.")
            return None

        extracted_courses = self.extract_courses_info(courses_data)
        self.save_courses_to_file(extracted_courses)

        gpa_result = self.calculate_gpa(extracted_courses)
        print("\nGPA Calculation Results:")
        print(f"Total Points: {gpa_result['total_points']}")
        print(f"Total Hours: {gpa_result['total_hours']}")
        print(f"GPA: {gpa_result['gpa']}")
        print(f"General Grade: {gpa_result['general_grade']}")
        print(f"Number of Courses Counted: {gpa_result['courses_count']}")

        return gpa_result


if __name__ == "__main__":
    # Example usage
    username = input("Enter your student ID: ")
    password = input("Enter your password: ")

    calculator = FCAIGPACalculator(username, password)
    gpa_result = calculator.run()
