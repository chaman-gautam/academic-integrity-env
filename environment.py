"""Academic Integrity Investigation Environment - OpenEnv compliant."""
import copy
from typing import Dict, Any, Tuple, List, Optional
from models import InvestigationObservation, InvestigationAction, InvestigationReward, InvestigationState
from tasks import CASES
from grader import grade

class AcademicIntegrityEnv:
    """
    Single-agent environment where an AI investigator gathers evidence and makes a ruling.
    Reward shaped for thoroughness, ethics, and efficiency.
    """
    
    def __init__(self, max_steps: int = 10):
        self.max_steps = max_steps
        self.task_id = None
        self.case = None
        self.step_count = 0
        self.collected_evidence = {}
        self.ruling_made = False
        self.final_ruling = None
        self.history = []  # list of actions taken
        
    def reset(self, task_id: str = "easy") -> InvestigationObservation:
        """Reset environment to start of a new case."""
        if task_id not in CASES:
            raise ValueError(f"Invalid task_id: {task_id}. Choose from {list(CASES.keys())}")
        self.task_id = task_id
        self.case = copy.deepcopy(CASES[task_id])
        self.step_count = 0
        self.collected_evidence = {}
        self.ruling_made = False
        self.final_ruling = None
        self.history = []
        # Set max steps from case or default
        self.max_steps = self.case.get("max_steps", 10)
        return self._get_observation()
    
    def _get_observation(self) -> InvestigationObservation:
        """Build current observation from internal state."""
        # Determine available actions
        available = ["request_similarity_report", "request_documents", "ask_student", "review_previous_cases"]
        if "instructor_statement" in self.case and self.case["instructor_statement"] is not None:
            available.append("ask_instructor")
        if len(self.collected_evidence) >= 2:  # after some evidence, allow ruling
            available.append("make_ruling")
        
        # Summarize evidence
        evidence_summary = f"Collected: {', '.join(self.collected_evidence.keys())}" if self.collected_evidence else "No evidence collected yet."
        
        statements = []
        if self.collected_evidence.get("student_statement"):
            statements.append(f"Student: {self.collected_evidence['student_statement']}")
        if self.collected_evidence.get("instructor_statement"):
            statements.append(f"Instructor: {self.collected_evidence['instructor_statement']}")
        
        # Compute current confidence based on evidence gathered (simple heuristic)
        required = set(self.case["required_evidence"])
        collected_set = set(self.collected_evidence.keys())
        confidence = len(collected_set & required) / len(required) if required else 0.5
        
        return InvestigationObservation(
            case_id=self.task_id,
            case_description=self.case["description"],
            available_actions=available,
            evidence_summary=evidence_summary,
            statements=statements,
            step_count=self.step_count,
            max_steps=self.max_steps,
            current_confidence=confidence
        )
    
    def step(self, action: InvestigationAction) -> Tuple[InvestigationObservation, float, bool, Dict]:
        """
        Execute an action, update state, compute reward, return (obs, reward, done, info).
        """
        if self.ruling_made:
            raise RuntimeError("Episode already finished. Call reset() first.")
        
        reward = 0.0
        info = {"action": action.action_type, "parameters": action.parameters}
        done = False
        
        # --- Process action ---
        if action.action_type == "request_similarity_report":
            if "similarity_report" not in self.collected_evidence:
                self.collected_evidence["similarity_report"] = self.case["similarity_report"]
                reward += 0.10  # evidence gain reward
                info["evidence_gain"] = 0.10
            else:
                reward -= 0.02  # penalty for repeated request
                info["repeat_penalty"] = -0.02
        
        elif action.action_type == "request_documents":
            if "documents" not in self.collected_evidence:
                self.collected_evidence["documents"] = self.case["documents"]
                reward += 0.05
                info["evidence_gain"] = 0.05
            else:
                reward -= 0.01
        
        elif action.action_type == "ask_student":
            if "student_statement" not in self.collected_evidence:
                self.collected_evidence["student_statement"] = self.case["student_statement"]
                reward += 0.10
                info["evidence_gain"] = 0.10
            else:
                reward -= 0.02
        
        elif action.action_type == "ask_instructor":
            if self.case["instructor_statement"] is None:
                reward -= 0.10  # invalid action in easy case
                info["invalid_action"] = -0.10
            elif "instructor_statement" not in self.collected_evidence:
                self.collected_evidence["instructor_statement"] = self.case["instructor_statement"]
                reward += 0.10
                info["evidence_gain"] = 0.10
            else:
                reward -= 0.02
        
        elif action.action_type == "review_previous_cases":
            if "previous_cases" not in self.collected_evidence and "previous_cases" in self.case:
                self.collected_evidence["previous_cases"] = self.case["previous_cases"]
                reward += 0.10  # reasoning bonus
                info["reasoning_bonus"] = 0.10
            else:
                reward += 0.02  # still a small positive for consulting policy even if not required
        
        elif action.action_type == "make_ruling":
            ruling = action.parameters.get("ruling")
            valid_rulings = ["no_violation", "warning", "grade_penalty", "course_failure"]
            if ruling not in valid_rulings:
                reward -= 0.20
                info["invalid_ruling"] = -0.20
                # Still end episode but with penalty
            else:
                self.final_ruling = ruling
                # Compute final grade using grader
                grader_score = grade(self.task_id, ruling, self.collected_evidence)
                # Final step reward = 0.5 * grader_score + ethical bonus if all required evidence collected
                ethical_bonus = 0.0
                required = set(self.case["required_evidence"])
                collected_set = set(self.collected_evidence.keys())
                if required.issubset(collected_set):
                    ethical_bonus = 0.20  # bonus for thoroughness
                final_reward = (0.5 * grader_score) + ethical_bonus
                reward += final_reward
                info["grader_score"] = grader_score
                info["ethical_bonus"] = ethical_bonus
                info["final_reward"] = final_reward
            self.ruling_made = True
            done = True
        
        else:
            reward -= 0.05  # unknown action penalty
            info["unknown_action"] = -0.05
        
        # --- Efficiency penalty (per step after step 3) ---
        if self.step_count >= 3:
            penalty = -0.01
            reward += penalty
            info["efficiency_penalty"] = penalty
        
        # Clamp reward to [-1, 1] for stability
        # reward = max(-1.0, min(1.0, reward))
        reward = max(0.0, min(1.0, reward))
        
        # Increment step counter
        self.step_count += 1
        self.history.append((action.action_type, reward))
        
        # Force done if max steps reached
        if self.step_count >= self.max_steps and not done:
            done = True
            # Penalty for not ruling
            reward -= 0.30
            info["timeout_penalty"] = -0.30
            # Also compute a default grader score (very low)
            if self.final_ruling is None:
                self.final_ruling = "no_violation"  # default
            grader_score = grade(self.task_id, self.final_ruling, self.collected_evidence)
            reward += 0.3 * grader_score  # partial credit
            info["forced_end"] = True
        
        obs = self._get_observation()
        return obs, reward, done, info
    
    def state(self) -> InvestigationState:
        """Return current internal state (for debugging or external logging)."""
        return InvestigationState(
            case_id=self.task_id,
            step=self.step_count,
            collected_evidence=self.collected_evidence,
            student_statement=self.collected_evidence.get("student_statement"),
            instructor_statement=self.collected_evidence.get("instructor_statement"),
            similarity_report=self.collected_evidence.get("similarity_report"),
            tentative_ruling=None,  # not used in this env
            ruling_made=self.ruling_made
        )
    
    def close(self):
        """Cleanup (no resources to free)."""
        pass