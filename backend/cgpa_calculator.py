# cgpa_calculator.py
import re
from collections import defaultdict

GRADE_POINTS = {
    "O": 10, "A+": 9, "A": 8, "B+": 7,
    "B": 6, "C": 5, "D": 4, "F": 0
}

GRADE_REGEX = re.compile(
    r"Grade:\s*(O|A\+|A|B\+|B|C|D|F)\s*—\s*Credits:\s*([\d.]+)",
    re.IGNORECASE
)

def calculate_cgpa_and_fails(docs, semester=None):
    total_points = 0.0
    total_credits = 0.0
    failed_subjects = 0

    for doc in docs:
        if semester and doc.metadata.get("semester") != semester:
            continue

        matches = GRADE_REGEX.findall(doc.page_content)

        for grade, credits in matches:
            grade = grade.upper()
            credits = float(credits)

            if grade == "F":
                failed_subjects += 1

            total_points += GRADE_POINTS[grade] * credits
            total_credits += credits

    if total_credits == 0:
        return None, failed_subjects, 0

    return round(total_points / total_credits, 2), failed_subjects, total_credits

def calculate_all_semester_gpa(docs):
    """
    returns:
    {
      "I Year I Sem": {"gpa": 8.85, "fails": 0, "credits": 19.5},
      "I Year II Sem": {...}
    }
    """
    semester_map = defaultdict(list)

    for doc in docs:
        sem = doc.metadata.get("semester")
        if sem:
            semester_map[sem].append(doc)

    results = {}

    for sem, sem_docs in semester_map.items():
        gpa, fails, credits = calculate_cgpa_and_fails(sem_docs)
        results[sem] = {
            "gpa": gpa,
            "fails": fails,
            "credits": credits
        }

    return results



