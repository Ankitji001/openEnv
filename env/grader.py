from .models import Action, Reward

def grade_easy(action: Action, ground_truth: dict) -> Reward:
    if not action.classification:
        return Reward(value=0.01, reason="Missing classification")
    
    if action.classification.lower() == ground_truth.get("classification", "").lower():
        return Reward(value=0.99, reason="Correct classification.")
    else:
        return Reward(value=0.01, reason=f"Incorrect classification. Expected {ground_truth.get('classification')}")

def grade_medium(action: Action, ground_truth: dict) -> Reward:
    score = 0.0
    reasons = []
    
    if action.classification and action.classification.lower() == ground_truth.get("classification", "").lower():
        score += 0.4
        reasons.append("Correct classification.")
    else:
        reasons.append("Incorrect classification.")
        
    if action.priority and action.priority.lower() == ground_truth.get("priority", "").lower():
        score += 0.3
        reasons.append("Correct priority.")
    else:
        reasons.append("Incorrect priority.")
        
    if action.action_choice and action.action_choice.lower() == ground_truth.get("action_choice", "").lower():
        score += 0.3
        reasons.append("Correct action.")
    else:
        reasons.append("Incorrect action.")
        
    # Floating point precision max 1.0
    score = min(max(round(score, 2), 0.01), 0.99)
    return Reward(value=score, reason=" ".join(reasons))

def grade_hard_step(action: Action, ground_truth: dict, processed_ids: set) -> Reward:
    if action.email_id in processed_ids:
        # Penalize repeated action
        return Reward(value=0.01, reason="Repeated action on already processed email.")
    
    medium_reward = grade_medium(action, ground_truth)
    
    # Check if incomplete action. Partial rewards allowed.
    components = [action.classification, action.priority, action.action_choice]
    missing = sum(1 for c in components if not c)
    if missing > 0:
        # Valid partial action but not fully completed
        medium_reward.value = max(0.01, medium_reward.value - (missing * 0.1))
        medium_reward.reason += f" Invalid or incomplete parts ({missing} missing)."
        
    medium_reward.value = min(max(round(medium_reward.value, 2), 0.01), 0.99)
    return medium_reward

def grade_easy_eval(action, ground_truth) -> float:
    """Float wrapper for Phase 2 evaluator"""
    import json
    if hasattr(action, "model_dump"): action = action.model_dump()
    elif hasattr(action, "dict"): action = action.dict()
    if isinstance(action, str):
        try: action = json.loads(action)
        except: return 0.01
    if not isinstance(action, dict): return 0.01

    if hasattr(ground_truth, "model_dump"): ground_truth = ground_truth.model_dump()
    elif hasattr(ground_truth, "dict"): ground_truth = ground_truth.dict()
    if not isinstance(ground_truth, dict): ground_truth = {}
    
    gt_class = ground_truth.get("classification")
    if gt_class is None: gt_class = ""
    else: gt_class = str(gt_class)
    
    class_val = action.get("classification")
    if class_val is None: class_val = ""
    else: class_val = str(class_val)
    
    if not class_val: return 0.01
    if class_val.lower() == gt_class.lower():
        return 0.99
    return 0.01

def grade_medium_eval(action, ground_truth) -> float:
    """Float wrapper for Phase 2 evaluator"""
    import json
    if hasattr(action, "model_dump"): action = action.model_dump()
    elif hasattr(action, "dict"): action = action.dict()
    if isinstance(action, str):
        try: action = json.loads(action)
        except: return 0.01
    if not isinstance(action, dict): return 0.01
    
    if hasattr(ground_truth, "model_dump"): ground_truth = ground_truth.model_dump()
    elif hasattr(ground_truth, "dict"): ground_truth = ground_truth.dict()
    if not isinstance(ground_truth, dict): ground_truth = {}
    
    score = 0.0
    
    act_cls = str(action.get("classification") or "")
    gt_cls = str(ground_truth.get("classification") or "")
    if act_cls and act_cls.lower() == gt_cls.lower():
        score += 0.4
        
    act_pri = str(action.get("priority") or "")
    gt_pri = str(ground_truth.get("priority") or "")
    if act_pri and act_pri.lower() == gt_pri.lower():
        score += 0.3
        
    act_act = str(action.get("action_choice") or "")
    gt_act = str(ground_truth.get("action_choice") or "")
    if act_act and act_act.lower() == gt_act.lower():
        score += 0.3
        
    return min(max(round(score, 2), 0.01), 0.99)

def grade_hard_eval(action, ground_truth) -> float:
    """Float wrapper for Phase 2 evaluator"""
    return grade_medium_eval(action, ground_truth)
