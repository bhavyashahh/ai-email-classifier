from env.models import Reward


FIELD_WEIGHTS = {
    1: {"spam_status": 1.0},
    2: {"spam_status": 0.5, "category": 0.5},
    3: {"spam_status": 0.34, "category": 0.33, "priority": 0.33},
}


def compute_reward(action: dict, ground_truth: dict, required_fields: list[str]) -> Reward:
    n = len(required_fields)
    weights = FIELD_WEIGHTS.get(n, {f: 1.0 / n for f in required_fields})

    breakdown = {}
    total = 0.0
    feedback_parts = []

    for field in required_fields:
        expected = _normalize(field, ground_truth.get(field, ""))
        actual = _normalize(field, action.get(field, ""))

        if actual == expected:
            score = 1.0
            feedback_parts.append(f"{field}: correct")
        elif _is_partial_match(field, actual, expected):
            score = 0.4
            feedback_parts.append(f"{field}: partial ({actual} vs {expected})")
        else:
            score = 0.0
            feedback_parts.append(f"{field}: wrong ({actual} vs {expected})")

        w = weights.get(field, 0.0)
        breakdown[field] = round(score * w, 3)
        total += score * w

    total = round(max(0.0, min(1.0, total)), 3)
    return Reward(total=total, breakdown=breakdown, feedback="; ".join(feedback_parts))


def _normalize(field: str, value: str) -> str:
    """Normalize agent output to match ground truth format."""
    v = value.lower().strip().strip('"').strip("'")
    if field == "spam_status":
        if v in ("spam", "yes", "true"):
            return "spam"
        if v in ("not spam", "not_spam", "no", "false", "ham", "legitimate"):
            return "not_spam"
    if field == "category":
        v = v.replace(" ", "")
        aliases = {"promotion": "promotions", "update": "updates", "financial": "finance"}
        return aliases.get(v, v)
    if field == "priority":
        v = v.replace(" ", "")
    return v


def _is_partial_match(field: str, actual: str, expected: str) -> bool:
    if field == "priority":
        order = ["low", "medium", "high"]
        if actual in order and expected in order:
            return abs(order.index(actual) - order.index(expected)) == 1
    if field == "category":
        close_pairs = [
            {"work", "updates"},
            {"personal", "promotions"},
            {"finance", "updates"},
        ]
        return {actual, expected} in close_pairs
    return False
