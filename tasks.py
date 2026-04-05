"""Predefined cases for each difficulty level."""
from typing import Dict, Any

CASES = {
    "easy": {
        "case_id": "case_001",
        "description": (
            "Student submitted an essay that has 80% similarity with a single online source. "
            "No citations are present. The student admits copying 'by accident' when confronted."
        ),
        "ground_truth": "grade_penalty",
        "required_evidence": ["similarity_report", "student_statement"],
        "student_statement": "I accidentally copied from a website without realizing it. I'm sorry.",
        "instructor_statement": None,  # Not required for easy
        "similarity_report": {"score": 0.80, "flagged_passages": ["entire introduction", "conclusion"]},
        "documents": "Essay.txt, source.html",
        "max_steps": 6
    },
    "medium": {
        "case_id": "case_002",
        "description": (
            "Student paraphrased several passages from multiple sources without citations. "
            "The student claims 'didn't know how to cite properly'. The instructor says "
            "previous warnings were given in class."
        ),
        "ground_truth": "warning",
        "required_evidence": ["similarity_report", "student_statement", "instructor_statement"],
        "student_statement": "I didn't know I had to cite paraphrased ideas. No one taught me.",
        "instructor_statement": "I gave a lecture on citations two weeks ago and posted a guide.",
        "similarity_report": {"score": 0.45, "flagged_passages": ["three paragraphs"]},
        "documents": "Essay.docx, sources.zip",
        "max_steps": 8
    },
    "hard": {
        "case_id": "case_003",
        "description": (
            "Student and friend submitted nearly identical code for a programming assignment. "
            "Both deny collusion. Metadata shows file creation times minutes apart. "
            "The student has a prior honor code violation on record."
        ),
        "ground_truth": "course_failure",
        "required_evidence": ["similarity_report", "student_statement", "instructor_statement", "documents", "previous_cases"],
        "student_statement": "We worked separately but used the same online tutorial.",
        "instructor_statement": "The code is identical including variable names and comments.",
        "similarity_report": {"score": 0.98, "flagged_passages": "entire file"},
        "documents": "student1.py, student2.py, metadata_logs.txt",
        "previous_cases": "Prior honor code violation for plagiarism in freshman year.",
        "max_steps": 10
    }
}