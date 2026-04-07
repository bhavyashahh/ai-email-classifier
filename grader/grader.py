import re
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load environment variables (looks for GEMINI_API_KEY)
load_dotenv()

# Initialize the Gemini Client
client = genai.Client()

# Weights for the three tasks
WEIGHTS = {"task1": 0.50, "task2": 0.30, "task3": 0.20}

GRADER_SYSTEM_PROMPT = """You are an expert grader evaluating an AI email-analysis agent's response.

You will receive the original email and the AI's answers for three tasks, each with a justification.

Grade each task on a scale from 0 to 1 using these rubrics:

TASK 1 — Spam Detection:
  1.0  Correct verdict AND justification cites specific signals (urgency language,
       prize claims, suspicious links, sender mismatch, unsubscribe pressure, etc.)
  0.7–0.9  Correct verdict but reasoning is vague or generic.
  0.4–0.6  Plausible verdict; reasoning weak or partially inconsistent.
  0.1–0.3  Likely wrong verdict OR reasoning contradicts it.
  0.0  Clearly wrong OR reasoning absent/incoherent.

TASK 2 — Category (Work / Personal / Promotions / Updates / Finance):
  1.0  Best-fitting category with clear, specific reasoning.
  0.7–0.9  Correct but reasoning is thin.
  0.4–0.6  Borderline choice; reasoning debatable.
  0.1–0.3  Poor fit; reasoning unsound.
  0.0  Completely wrong OR no reasoning.

TASK 3 — Priority (High / Medium / Low):
  1.0  Most appropriate level with clear reasoning tied to urgency/importance.
  0.7–0.9  Reasonable but reasoning could be sharper.
  0.4–0.6  Debatable; partially justified.
  0.1–0.3  Likely wrong; reasoning contradicts the chosen level.
  0.0  Clearly wrong OR absent/incoherent.

Respond in EXACTLY this format (no extra text, no markdown):

TASK1_GRADE: <number 0–1>
TASK1_EXPLANATION: <one sentence>

TASK2_GRADE: <number 0–1>
TASK2_EXPLANATION: <one sentence>

TASK3_GRADE: <number 0–1>
TASK3_EXPLANATION: <one sentence>"""


def _safe_float(text: str, default: float = 0.0) -> float:
    """Extract the first float from a string and clamp to [0, 1]."""
    match = re.search(r"\d+\.?\d*", text)
    if match:
        return max(0.0, min(1.0, float(match.group())))
    return default


def grade_response(email: str, agent_result: dict) -> dict:
    """
    Grades all three tasks in a single Gemini call.
    """

    user_message = (
        f"EMAIL:\n{email}\n\n"
        f"TASK 1 - Spam Status: {agent_result.get('spam_status', '')}\n"
        f"Justification: {agent_result.get('spam_justification', '')}\n\n"
        f"TASK 2 - Category: {agent_result.get('category', '')}\n"
        f"Justification: {agent_result.get('category_justification', '')}\n\n"
        f"TASK 3 - Priority: {agent_result.get('priority', '')}\n"
        f"Justification: {agent_result.get('priority_justification', '')}"
    )

    # Call the Gemini API
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=user_message,
        config=types.GenerateContentConfig(
            system_instruction=GRADER_SYSTEM_PROMPT,
            temperature=0.0 # Set to 0.0 to ensure strict, deterministic grading formats
        )
    )

    # Extract text from the Gemini response
    raw = response.text.strip()

    grades = {
        "task1_grade": 0.0,
        "task1_explanation": "",
        "task2_grade": 0.0,
        "task2_explanation": "",
        "task3_grade": 0.0,
        "task3_explanation": "",
        "raw": raw,
    }

    for line in [l.strip() for l in raw.splitlines() if l.strip()]:
        upper = line.upper()

        if upper.startswith("TASK1_GRADE:"):
            grades["task1_grade"] = _safe_float(line.split(":", 1)[1])

        elif upper.startswith("TASK1_EXPLANATION:"):
            grades["task1_explanation"] = line.split(":", 1)[1].strip()

        elif upper.startswith("TASK2_GRADE:"):
            grades["task2_grade"] = _safe_float(line.split(":", 1)[1])

        elif upper.startswith("TASK2_EXPLANATION:"):
            grades["task2_explanation"] = line.split(":", 1)[1].strip()

        elif upper.startswith("TASK3_GRADE:"):
            grades["task3_grade"] = _safe_float(line.split(":", 1)[1])

        elif upper.startswith("TASK3_EXPLANATION:"):
            grades["task3_explanation"] = line.split(":", 1)[1].strip()

    grades["overall_grade"] = round(
        WEIGHTS["task1"] * grades["task1_grade"]
        + WEIGHTS["task2"] * grades["task2_grade"]
        + WEIGHTS["task3"] * grades["task3_grade"],
        2,
    )

    return grades


def grade_label(grade: float) -> str:
    """Returns a human-readable performance label."""
    if grade >= 0.90:
        return "Excellent"
    elif grade >= 0.70:
        return "Good"
    elif grade >= 0.50:
        return "Partial"
    elif grade >= 0.20:
        return "Poor"
    else:
        return "Fail"


# --- Optional: Local Testing ---
if __name__ == "__main__":
    # Mocking the agent result for standalone testing
    # In reality, this comes from agent.geminiai_agent.get_email_analysis
    email = "Hi team, please review the Q3 report and approve by EOD Friday. Urgent."
    mock_agent_result = {
        "spam_status": "Not Spam",
        "spam_justification": "It is an internal team request about Q3 reports.",
        "category": "Work",
        "category_justification": "Discusses reports and approvals.",
        "priority": "High",
        "priority_justification": "Mentions EOD Friday and is marked Urgent."
    }
    
    grade_result = grade_response(email, mock_agent_result)

    print(f"Task 1  : {grade_result['task1_grade']:.2f}  — {grade_result['task1_explanation']}")
    print(f"Task 2  : {grade_result['task2_grade']:.2f}  — {grade_result['task2_explanation']}")
    print(f"Task 3  : {grade_result['task3_grade']:.2f}  — {grade_result['task3_explanation']}")
    print(f"Overall : {grade_result['overall_grade']:.2f}  [{grade_label(grade_result['overall_grade'])}]")