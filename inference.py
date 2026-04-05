# #!/usr/bin/env python3
# """Baseline inference script using OpenAI client. Logs in [START]/[STEP]/[END] format."""
# import asyncio
# import os
# import textwrap
# from typing import List, Optional
# from openai import OpenAI
# from environment import AcademicIntegrityEnv
# from models import InvestigationAction

# # ----------------------------------------------------------------------
# # Environment variables (must be set)
# # ----------------------------------------------------------------------
# API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
# MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
# HF_TOKEN = os.getenv("HF_TOKEN")
# API_KEY = HF_TOKEN or os.getenv("API_KEY")

# # If using Docker image for env, we can instantiate directly (no Docker needed for inference script)
# # But for HF Space, we'll call the HTTP endpoints. For simplicity, we use local env class.
# # The hackathon expects inference.py to run against the environment (local or remote).
# # We'll use the local environment class directly (no extra container).

# TASKS = ["easy", "medium", "hard"]
# MAX_STEPS_PER_TASK = 10
# TEMPERATURE = 0.7

# SYSTEM_PROMPT = textwrap.dedent(
#     """
#     You are an academic integrity investigator. You must gather evidence and then make a ruling.
#     Available actions: request_similarity_report, request_documents, ask_student, ask_instructor, review_previous_cases, make_ruling.
#     When making a ruling, choose from: no_violation, warning, grade_penalty, course_failure.
#     Be thorough: collect all relevant evidence before ruling. Penalty for ruling too early.
#     Respond with a JSON object: {"action": "<action_type>", "parameters": {}}.
#     Example: {"action": "request_similarity_report", "parameters": {}}
#     Example: {"action": "make_ruling", "parameters": {"ruling": "warning"}}
#     """
# ).strip()

# def log_start(task: str, env: str, model: str) -> None:
#     print(f"[START] task={task} env={env} model={model}", flush=True)

# def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
#     error_str = error if error else "null"
#     done_str = str(done).lower()
#     print(f"[STEP] step={step} action={action} reward={reward:.2f} done={done_str} error={error_str}", flush=True)

# def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
#     rewards_str = ",".join(f"{r:.2f}" for r in rewards)
#     print(f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}", flush=True)

# def get_model_action(client: OpenAI, observation_text: str, step: int) -> str:
#     """Call LLM to decide next action. Returns JSON string."""
#     user_prompt = f"Step {step}\nObservation: {observation_text}\nWhat action do you take? Respond with JSON."
#     try:
#         completion = client.chat.completions.create(
#             model=MODEL_NAME,
#             messages=[
#                 {"role": "system", "content": SYSTEM_PROMPT},
#                 {"role": "user", "content": user_prompt},
#             ],
#             temperature=TEMPERATURE,
#             max_tokens=150,
#         )
#         content = completion.choices[0].message.content.strip()
#         # Extract JSON from possible markdown
#         if "```json" in content:
#             content = content.split("```json")[1].split("```")[0].strip()
#         elif "```" in content:
#             content = content.split("```")[1].split("```")[0].strip()
#         return content
#     except Exception as e:
#         print(f"[DEBUG] LLM call failed: {e}", flush=True)
#         # Fallback action
#         return '{"action": "request_similarity_report", "parameters": {}}'

# async def run_task(task_name: str, env: AcademicIntegrityEnv, client: OpenAI) -> tuple[float, List[float], int]:
#     """Run one episode for a given task. Returns (total_score, rewards_list, steps_taken)."""
#     obs = env.reset(task_name)
#     step = 0
#     rewards = []
#     done = False
#     error = None
    
#     while step < MAX_STEPS_PER_TASK and not done:
#         # Convert observation to text for LLM
#         obs_text = f"Case: {obs.case_description}\nEvidence: {obs.evidence_summary}\nStatements: {obs.statements}\nAvailable actions: {obs.available_actions}"
#         action_json = get_model_action(client, obs_text, step+1)
        
#         # Parse JSON
#         try:
#             import json
#             action_dict = json.loads(action_json)
#             action_type = action_dict.get("action")
#             params = action_dict.get("parameters", {})
#             action = InvestigationAction(action_type=action_type, parameters=params)
#         except Exception as e:
#             error = f"JSON parse error: {e}"
#             # Fallback safe action
#             action = InvestigationAction(action_type="request_similarity_report", parameters={})
        
#         # Take step
#         obs, reward, done, info = env.step(action)
#         rewards.append(reward)
#         step += 1
#         log_step(step=step, action=action_json, reward=reward, done=done, error=error)
#         error = None  # reset after logging
    
#     # After episode ends, compute final score (normalized to 0-1). For baseline, we can use the grader score from final step.
#     # But we don't have direct access to grader here. Instead, we'll compute a simple score based on final ruling correctness.
#     # To be reproducible, we call grade() manually.
#     from grader import grade
#     final_score = grade(task_name, env.final_ruling if env.final_ruling else "no_violation", env.collected_evidence)
#     return final_score, rewards, step

# async def main():
#     # Initialize OpenAI client
#     client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
#     env = AcademicIntegrityEnv()
    
#     all_scores = []
#     all_rewards = []
    
#     for task in TASKS:
#         log_start(task=task, env="academic_integrity_env", model=MODEL_NAME)
#         score, rewards, steps = await run_task(task, env, client)
#         all_scores.append(score)
#         all_rewards.extend(rewards)
#         success = score >= 0.5  # threshold for success
#         log_end(success=success, steps=steps, score=score, rewards=rewards)
#         print()  # blank line between tasks
    
#     # Optional: print overall average
#     avg_score = sum(all_scores) / len(all_scores) if all_scores else 0.0
#     print(f"Baseline average score: {avg_score:.3f}", flush=True)
#     await env.close()

# if __name__ == "__main__":
#     asyncio.run(main())



#!/usr/bin/env python3
"""Baseline inference script using OpenAI client. Logs in [START]/[STEP]/[END] format."""
import asyncio
import os
import json
import textwrap
from typing import List, Optional
from openai import OpenAI
from environment import AcademicIntegrityEnv
from models import InvestigationAction

# ----------------------------------------------------------------------
# Environment variables
# ----------------------------------------------------------------------
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
HF_TOKEN = os.getenv("HF_TOKEN")
API_KEY = HF_TOKEN or os.getenv("OPENAI_API_KEY")  # also support OPENAI_API_KEY

TASKS = ["easy", "medium", "hard"]
MAX_STEPS_PER_TASK = 10
TEMPERATURE = 0.7

SYSTEM_PROMPT = textwrap.dedent(
    """
    You are an academic integrity investigator. You must gather evidence and then make a ruling.
    Available actions: request_similarity_report, request_documents, ask_student, ask_instructor, review_previous_cases, make_ruling.
    When making a ruling, choose from: no_violation, warning, grade_penalty, course_failure.
    Be thorough: collect all relevant evidence before ruling. Penalty for ruling too early.
    Respond with a JSON object: {"action": "<action_type>", "parameters": {}}.
    Example: {"action": "request_similarity_report", "parameters": {}}
    Example: {"action": "make_ruling", "parameters": {"ruling": "warning"}}
    """
).strip()

def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_str = error if error else "null"
    done_str = str(done).lower()
    print(f"[STEP] step={step} action={action} reward={reward:.2f} done={done_str} error={error_str}", flush=True)

def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}", flush=True)

def get_model_action(client: OpenAI, observation_text: str, step: int) -> str:
    """Call LLM to decide next action. Returns JSON string."""
    user_prompt = f"Step {step}\nObservation: {observation_text}\nWhat action do you take? Respond with JSON."
    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=TEMPERATURE,
            max_tokens=150,
        )
        content = completion.choices[0].message.content.strip()
        # Extract JSON from possible markdown
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        return content
    except Exception as e:
        print(f"[DEBUG] LLM call failed: {e}", flush=True)
        return '{"action": "request_similarity_report", "parameters": {}}'

async def run_task(task_name: str, env: AcademicIntegrityEnv, client: OpenAI) -> tuple[float, List[float], int]:
    obs = env.reset(task_name)
    step = 0
    rewards = []
    done = False
    error = None

    while step < MAX_STEPS_PER_TASK and not done:
        obs_text = f"Case: {obs.case_description}\nEvidence: {obs.evidence_summary}\nStatements: {obs.statements}\nAvailable actions: {obs.available_actions}"
        action_json = get_model_action(client, obs_text, step+1)

        try:
            action_dict = json.loads(action_json)
            action_type = action_dict.get("action")
            params = action_dict.get("parameters", {})
            action = InvestigationAction(action_type=action_type, parameters=params)
        except Exception as e:
            error = f"JSON parse error: {e}"
            action = InvestigationAction(action_type="request_similarity_report", parameters={})

        obs, reward, done, info = env.step(action)
        rewards.append(reward)
        step += 1
        log_step(step=step, action=action_json, reward=reward, done=done, error=error)
        error = None

    from grader import grade
    final_score = grade(task_name, env.final_ruling if env.final_ruling else "no_violation", env.collected_evidence)
    return final_score, rewards, step

async def main():
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    env = AcademicIntegrityEnv()

    all_scores = []
    for task in TASKS:
        log_start(task=task, env="academic_integrity_env", model=MODEL_NAME)
        score, rewards, steps = await run_task(task, env, client)
        all_scores.append(score)
        success = score >= 0.5
        log_end(success=success, steps=steps, score=score, rewards=rewards)
        print()

    avg_score = sum(all_scores) / len(all_scores) if all_scores else 0.0
    print(f"Baseline average score: {avg_score:.3f}", flush=True)
    env.close()   # <-- FIXED: removed await (close is synchronous)

if __name__ == "__main__":
    asyncio.run(main())