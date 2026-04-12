import json
from typing import List, Dict, Any

def load_emails(filepath: str = "data/emails.json") -> List[Dict[str, Any]]:
    with open(filepath, "r") as f:
        return json.load(f)

# Task definitions map to different difficulty levels.
TASKS = {
    "easy": {
        "description": "Classify a single email into spam, urgent, or normal.",
        "requires_priority": False,
        "requires_action": False,
        "sequential": False
    },
    "medium": {
        "description": "Classify an email, assign a priority, and choose an action.",
        "requires_priority": True,
        "requires_action": True,
        "sequential": False
    },
    "hard": {
        "description": "Sequentially process a queue of emails with full actions. Maintain state across steps and avoid invalid or repeated actions.",
        "requires_priority": True,
        "requires_action": True,
        "sequential": True
    }
}
