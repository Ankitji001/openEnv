
import json
from typing import List, Dict, Any

def load_emails(filepath: str = "data/emails.json") -> List[Dict[str, Any]]:
    with open(filepath, "r") as f:
        return json.load(f)

# Task definitions (metadata)
TASKS = {
    "easy": {
        "description": "Classify a single email into spam, urgent, or normal.",
        "requires_priority": False,
        "requires_action": False,
        "sequential": False,
        "grader": "grade_easy_eval"
    },
    "medium": {
        "description": "Classify an email, assign a priority, and choose an action.",
        "requires_priority": True,
        "requires_action": True,
        "sequential": False,
        "grader": "grade_medium_eval"
    },
    "hard": {
        "description": "Sequentially process a queue of emails with full actions. Maintain state across steps and avoid invalid or repeated actions.",
        "requires_priority": True,
        "requires_action": True,
        "sequential": True,
        "grader": "grade_hard_eval"
    }
}

# ✅ Explicit evaluation tasks (VERY IMPORTANT for Phase 2)
EVAL_TASKS = [
    {
        "id": "task_easy_1",
        "task_type": "easy",
        "grader": "grade_easy_eval"
    },
    {
        "id": "task_medium_1",
        "task_type": "medium",
        "grader": "grade_medium_eval"
    },
    {
        "id": "task_hard_1",
        "task_type": "hard",
        "grader": "grade_hard_eval"
    }
]

