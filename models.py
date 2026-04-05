"""Pydantic models for OpenEnv compliance."""
from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field

# ----------------------------------------------------------------------
# Observation
# ----------------------------------------------------------------------
class InvestigationObservation(BaseModel):
    case_id: str = Field(description="Unique identifier of the case")
    case_description: str = Field(description="Brief summary of the allegation")
    available_actions: List[str] = Field(description="Actions currently allowed")
    evidence_summary: str = Field(description="Text summary of gathered evidence so far")
    statements: List[str] = Field(description="Statements collected from student/instructor")
    step_count: int = Field(description="Number of steps taken")
    max_steps: int = Field(description="Maximum steps before forced episode end")
    current_confidence: float = Field(description="Agent's confidence in tentative ruling (0-1)", ge=0, le=1)

# ----------------------------------------------------------------------
# Action
# ----------------------------------------------------------------------
class InvestigationAction(BaseModel):
    action_type: Literal[
        "request_similarity_report",
        "request_documents",
        "ask_student",
        "ask_instructor",
        "review_previous_cases",
        "make_ruling"
    ] = Field(description="Type of investigative action")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Action parameters, e.g., {'ruling': 'warning'}")

# ----------------------------------------------------------------------
# Reward (optional but included for completeness)
# ----------------------------------------------------------------------
class InvestigationReward(BaseModel):
    value: float = Field(description="Reward value for the step")
    info: Dict[str, Any] = Field(default_factory=dict, description="Additional info (evidence gain, ethics, etc.)")

# ----------------------------------------------------------------------
# State (for state() method)
# ----------------------------------------------------------------------
class InvestigationState(BaseModel):
    case_id: str
    step: int
    collected_evidence: Dict[str, Any]   # e.g., {'similarity_report': {...}, 'student_statement': '...'}
    student_statement: Optional[str]
    instructor_statement: Optional[str]
    similarity_report: Optional[Dict]
    tentative_ruling: Optional[str]
    ruling_made: bool