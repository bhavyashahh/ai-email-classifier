from env.tasks import TASKS


def grade_task(task_id: str, actions: list[dict]) -> dict:
    """
    Deterministic grader: compares agent actions against ground truth.
    Returns score 0.0-1.0 and per-step details.
    """
    if task_id not in TASKS:
        return {"score": 0.0, "error": f"Unknown task: {task_id}"}

    task = TASKS[task_id]
    emails = task["emails"]
    required_fields = task["required_fields"]

    if len(actions) != len(emails):
        return {
            "score": 0.0,
            "error": f"Expected {len(emails)} actions, got {len(actions)}",
        }

    step_scores = []
    details = []

    for i, (email, action) in enumerate(zip(emails, actions)):
        gt = email["ground_truth"]
        correct = 0
        total = len(required_fields)
        step_detail = {"step": i}

        for field in required_fields:
            expected = gt.get(field, "").lower().strip()
            actual = action.get(field, "").lower().strip()
            match = actual == expected
            if match:
                correct += 1
            step_detail[field] = {
                "expected": expected,
                "actual": actual,
                "correct": match,
            }

        step_score = correct / total if total > 0 else 0.0
        step_scores.append(step_score)
        step_detail["score"] = round(step_score, 3)
        details.append(step_detail)

    avg_score = round(sum(step_scores) / len(step_scores), 3) if step_scores else 0.0

    return {"score": avg_score, "steps": details}
