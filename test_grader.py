# Standalone test - only tests the grader logic without importing env package
# Copies the grader logic inline to avoid the heavy openenv imports

import json

# === Inline copy of grade_easy_eval ===
def grade_easy_eval(action, ground_truth):
    if hasattr(action, "model_dump"): action = action.model_dump()
    if isinstance(action, str):
        try: action = json.loads(action)
        except: return 0.01
    if not isinstance(action, dict): return 0.01
    if hasattr(ground_truth, "model_dump"): ground_truth = ground_truth.model_dump()
    if not isinstance(ground_truth, dict): ground_truth = {}
    class_val = action.get("classification", "")
    if not class_val: return 0.01
    if class_val.lower() == ground_truth.get("classification", "").lower():
        return 0.99
    return 0.01

def grade_medium_eval(action, ground_truth):
    if hasattr(action, "model_dump"): action = action.model_dump()
    if isinstance(action, str):
        try: action = json.loads(action)
        except: return 0.01
    if not isinstance(action, dict): return 0.01
    if hasattr(ground_truth, "model_dump"): ground_truth = ground_truth.model_dump()
    if not isinstance(ground_truth, dict): ground_truth = {}
    score = 0.0
    if action.get("classification") and action.get("classification").lower() == ground_truth.get("classification", "").lower():
        score += 0.4
    if action.get("priority") and action.get("priority").lower() == ground_truth.get("priority", "").lower():
        score += 0.3
    if action.get("action_choice") and action.get("action_choice").lower() == ground_truth.get("action_choice", "").lower():
        score += 0.3
    return min(max(round(score, 2), 0.01), 0.99)

def grade_hard_eval(action, ground_truth):
    return grade_medium_eval(action, ground_truth)

# ===== TESTS =====
results = []
a_perfect = {'classification': 'spam', 'priority': 'low', 'action_choice': 'ignore'}
gt = {'classification': 'spam', 'priority': 'low', 'action_choice': 'ignore'}
a_wrong = {'classification': 'urgent', 'priority': 'high', 'action_choice': 'reply'}
a_empty = {}
a_json_str = '{"classification": "spam", "priority": "low", "action_choice": "ignore"}'

tests = {
    'easy_perfect_dict':      grade_easy_eval(a_perfect, gt),
    'medium_perfect_dict':    grade_medium_eval(a_perfect, gt),
    'hard_perfect_dict':      grade_hard_eval(a_perfect, gt),
    'easy_wrong_dict':        grade_easy_eval(a_wrong, gt),
    'medium_wrong_dict':      grade_medium_eval(a_wrong, gt),
    'easy_empty_dict':        grade_easy_eval(a_empty, gt),
    'medium_empty_dict':      grade_medium_eval(a_empty, gt),
    'easy_json_string':       grade_easy_eval(a_json_str, gt),
    'medium_json_string':     grade_medium_eval(a_json_str, gt),
    'easy_none':              grade_easy_eval(None, gt),
}

all_pass = True
for name, val in tests.items():
    strictly_ok = isinstance(val, (int, float)) and 0.0 < float(val) < 1.0
    status = "PASS" if strictly_ok else "FAIL"
    if not strictly_ok: all_pass = False
    results.append(f"[{status}] {name} = {val} (type={type(val).__name__})")

results.append("")
results.append(f"OVERALL: {'ALL PASS' if all_pass else 'SOME FAILED'}")

output = '\n'.join(results)
with open('grader_test_results.txt', 'w', encoding='utf-8') as f:
    f.write(output)
print(output)
