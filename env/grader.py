
from .models import Action, Reward

# ---------------- SAFE SCORE ----------------
def _safe_score(score: float) -> float:
    try:
        score = float(score)
    except:
        return 0.01

    return max(0.01, min(0.99, round(score, 2)))


# ---------------- TRAINING GRADERS (USED BY ENV) ----------------
def grade_easy(action: Action, ground_truth: dict) -> Reward:
    if not action.classification:
        return Reward(value=0.01, reason="Missing classification")

    if action.classification.lower() == str(ground_truth.get("classification", "")).lower():
        return Reward(value=0.99, reason="Correct classification.")
    return Reward(value=0.01, reason="Incorrect classification")


def grade_medium(action: Action, ground_truth: dict) -> Reward:
    score = 0.01  # 🔥 never 0
    reasons = []

    if action.classification and action.classification.lower() == str(ground_truth.get("classification", "")).lower():
        score += 0.4
        reasons.append("Correct classification.")
    else:
        reasons.append("Incorrect classification.")

    if action.priority and action.priority.lower() == str(ground_truth.get("priority", "")).lower():
        score += 0.3
        reasons.append("Correct priority.")
    else:
        reasons.append("Incorrect priority.")

    if action.action_choice and action.action_choice.lower() == str(ground_truth.get("action_choice", "")).lower():
        score += 0.3
        reasons.append("Correct action.")
    else:
        reasons.append("Incorrect action.")

    return Reward(value=_safe_score(score), reason=" ".join(reasons))


def grade_hard_step(action: Action, ground_truth: dict, processed_ids: set) -> Reward:
    if action.email_id in processed_ids:
        return Reward(value=0.01, reason="Repeated action")

    reward = grade_medium(action, ground_truth)

    components = [action.classification, action.priority, action.action_choice]
    missing = sum(1 for c in components if not c)

    if missing > 0:
        reward.value = max(0.01, reward.value - (missing * 0.1))
        reward.reason += f" Missing parts ({missing})"

    reward.value = _safe_score(reward.value)
    return reward


# ---------------- EVAL GRADERS (USED BY PHASE 2) ----------------
def grade_easy_eval(action, ground_truth) -> float:
    import json

    try:
        if hasattr(action, "model_dump"): action = action.model_dump()
        elif hasattr(action, "dict"): action = action.dict()
        if isinstance(action, str):
            action = json.loads(action)
        if not isinstance(action, dict):
            return 0.01

        if hasattr(ground_truth, "model_dump"): ground_truth = ground_truth.model_dump()
        elif hasattr(ground_truth, "dict"): ground_truth = ground_truth.dict()
        if not isinstance(ground_truth, dict):
            ground_truth = {}

        act = str(action.get("classification") or "")
        gt = str(ground_truth.get("classification") or "")

        if not act:
            return 0.01

        score = 0.99 if act.lower() == gt.lower() else 0.01
        return _safe_score(score)

    except:
        return 0.01


def grade_medium_eval(action, ground_truth) -> float:
    import json

    try:
        if hasattr(action, "model_dump"): action = action.model_dump()
        elif hasattr(action, "dict"): action = action.dict()
        if isinstance(action, str):
            action = json.loads(action)
        if not isinstance(action, dict):
            return 0.01

        if hasattr(ground_truth, "model_dump"): ground_truth = ground_truth.model_dump()
        elif hasattr(ground_truth, "dict"): ground_truth = ground_truth.dict()
        if not isinstance(ground_truth, dict):
            ground_truth = {}

        score = 0.01  # 🔥 never 0

        if str(action.get("classification") or "").lower() == str(ground_truth.get("classification") or "").lower():
            score += 0.4

        if str(action.get("priority") or "").lower() == str(ground_truth.get("priority") or "").lower():
            score += 0.3

        if str(action.get("action_choice") or "").lower() == str(ground_truth.get("action_choice") or "").lower():
            score += 0.3

        return _safe_score(score)

    except:
        return 0.01


def grade_hard_eval(action, ground_truth) -> float:
    return _safe_score(grade_medium_eval(action, ground_truth))

