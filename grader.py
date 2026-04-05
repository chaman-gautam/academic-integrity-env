"""Programmatic grader: returns score 0.0–1.0 based on ruling correctness and evidence completeness."""
from typing import Dict, Any

def grade(case_id: str, agent_ruling: str, collected_evidence: Dict[str, Any]) -> float:
    """
    Grade the agent's performance.
    
    Args:
        case_id: one of "easy", "medium", "hard"
        agent_ruling: one of "no_violation", "warning", "grade_penalty", "course_failure"
        collected_evidence: dict with keys like "similarity_report", "student_statement", etc.
    
    Returns:
        score in [0, 1]
    """
    from tasks import CASES
    case = CASES[case_id]
    ground_truth = case["ground_truth"]
    required = set(case["required_evidence"])
    
    # 1. Correctness weight = 0.7
    correctness = 0.7 if agent_ruling == ground_truth else 0.0
    
    # 2. Evidence completeness weight = 0.3
    evidence_collected = set(collected_evidence.keys())
    completeness = len(evidence_collected & required) / len(required) if required else 1.0
    evidence_score = completeness * 0.3
    
    total = correctness + evidence_score
    return round(min(1.0, total), 2)