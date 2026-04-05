# Academic Integrity Investigation Environment

An OpenEnv environment where an AI agent acts as a university academic misconduct investigator. The agent must gather evidence (similarity report, student/instructor statements, documents, prior cases) and then issue a ruling. The reward function encourages thorough, ethical, and efficient investigations.

## Real-World Utility

Academic misconduct cases are common in higher education. Automating parts of the investigation process can help standardize decisions, reduce bias, and train new investigators. This environment allows AI agents to learn investigative reasoning in a safe, reproducible setting.

## Action Space

- `request_similarity_report` – Get similarity score and flagged passages.
- `request_documents` – Obtain original submissions and source materials.
- `ask_student` – Get the student's statement.
- `ask_instructor` – Get the instructor's perspective (not available in easy case).
- `review_previous_cases` – Consult past cases (adds reasoning bonus).
- `make_ruling` – End the episode with a ruling: `no_violation`, `warning`, `grade_penalty`, or `course_failure`.

## Observation Space

- `case_description` – Text summary of the allegation.
- `available_actions` – Which actions are currently allowed.
- `evidence_summary` – What evidence has been collected.
- `statements` – List of collected statements.
- `step_count` / `max_steps`
- `current_confidence` – Heuristic measure of evidence completeness.

## Reward System (Unique Features)

| Component           | Value                   | Description                                 |
| ------------------- | ----------------------- | ------------------------------------------- |
| Evidence gain       | +0.05 to +0.15          | First time collecting each evidence type    |
| Repeat penalty      | -0.01 to -0.02          | Discourages redundant actions               |
| Reasoning bonus     | +0.10                   | Using `review_previous_cases`               |
| Procedural penalty  | -0.20                   | Ruling without mandatory evidence           |
| Efficiency penalty  | -0.01/step after step 3 | Encourages timely resolution                |
| Ethical bonus       | +0.20                   | Ruling with all required evidence collected |
| Final ruling reward | 0.5 × grader score      | Correctness + evidence completeness         |

The total reward per step is clamped to [-1, 1]. The episode ends after `make_ruling` or at `max_steps`.

## Tasks (Easy → Medium → Hard)

| Difficulty | Case Summary                                                             | Ground Truth     | Required Evidence                                                                     |
| ---------- | ------------------------------------------------------------------------ | ---------------- | ------------------------------------------------------------------------------------- |
| Easy       | 80% similarity, student admits accidental copying                        | `grade_penalty`  | similarity report, student statement                                                  |
| Medium     | Paraphrased passages, student claims ignorance, instructor gave warnings | `warning`        | similarity report, student statement, instructor statement                            |
| Hard       | Identical code, both deny collusion, prior violation                     | `course_failure` | similarity report, student statement, instructor statement, documents, previous cases |

Each task has a deterministic grader that returns a score 0.0–1.0 based on ruling correctness (70%) and evidence completeness (30%).

## Setup & Usage

### Local Installation

```bash
git clone <repo>
cd academic-integrity-env
pip install -r requirements.txt
```
