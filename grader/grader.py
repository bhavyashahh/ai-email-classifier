"""
grader/grader.py
----------------
Evaluates the AI agent's spam-classification response and returns a grade
between 0 and 1, plus a short explanation of the grade.

Grading rubric (sent to the grader LLM):
  1.0  – Correct, confident verdict backed by specific, accurate signals.
  0.7–0.9 – Correct verdict, but reasoning is somewhat vague or misses
             key signals while still being partially correct.
  0.4–0.6 – Verdict seems plausible but reasoning is weak, circular,
             or internally inconsistent.
  0.1–0.3 – Verdict is questionable or reasoning contradicts the verdict.
  0.0  – Verdict is clearly wrong OR reasoning is completely absent /
          nonsensical.
"""

import re
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

client = genai.Client()

GRADER_SYSTEM_PROMPT = """You are an expert grader evaluating an AI spam-classifier's response.

You will receive:
  EMAIL: the original email the AI was shown
  VERDICT: what the AI decided (spam or not spam)
  REASONING: the AI's justification

Your job is to grade the AI's response on a scale from 0 to 1 using this rubric:

  1.0  — Verdict is correct AND reasoning cites specific, accurate signals
           (e.g. suspicious links, urgency language, prize claims, sender mismatch).
  0.7–0.9 — Correct verdict but reasoning is vague, generic, or misses
              important signals.
  0.4–0.6 — Verdict is plausible but reasoning is weak, circular, or
              partially contradicts the verdict.
  0.1–0.3 — Verdict is likely wrong OR reasoning seriously contradicts it.
  0.0  — Verdict is clearly wrong OR reasoning is absent / incoherent.

Respond in EXACTLY this format (no extra text):

GRADE: <a number between 0 and 1, e.g. 0.75>
EXPLANATION: <one or two sentences explaining why you gave this grade>"""


def grade_response(email: str, verdict: str, reasoning: str) -> dict:
    """
    Grades the AI agent's classification response.

    Args:
        email    : the original email content
        verdict  : the agent's verdict ("spam" / "not spam")
        reasoning: the agent's reasoning string

    Returns a dict with:
        - grade      : float between 0.0 and 1.0
        - explanation: short string explaining the grade
        - raw        : raw grader response (for debugging)
    """
    user_message = (
        f"EMAIL:\n{email}\n\n"
        f"VERDICT: {verdict}\n\n"
        f"REASONING: {reasoning}"
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=user_message,
        config=types.GenerateContentConfig(
            system_instruction=GRADER_SYSTEM_PROMPT
        ),
    )

    raw = response.text.strip()
    grade = None
    explanation = ""

    for line in raw.splitlines():
        line = line.strip()
        if line.upper().startswith("GRADE:"):
            try:
                grade = float(line.split(":", 1)[1].strip())
                grade = max(0.0, min(1.0, grade))   # clamp to [0, 1]
            except ValueError:
                # Try to extract any float in the line
                match = re.search(r"\d+\.?\d*", line)
                if match:
                    grade = float(match.group())
                    grade = max(0.0, min(1.0, grade))
        elif line.upper().startswith("EXPLANATION:"):
            explanation = line.split(":", 1)[1].strip()

    if grade is None:
        grade = 0.0
        explanation = "Grader could not parse a valid grade. Defaulting to 0."

    return {
        "grade": grade,
        "explanation": explanation,
        "raw": raw,
    }


def grade_label(grade: float) -> str:
    """Returns a human-readable label for a numeric grade."""
    if grade >= 0.9:
        return "Excellent"
    elif grade >= 0.7:
        return "Good"
    elif grade >= 0.4:
        return "Partial"
    elif grade >= 0.1:
        return "Poor"
    else:
        return "Fail"


# --- Optional: Local Testing ---
if __name__ == "__main__":
    email = "CONGRATULATIONS! You've won a $1000 gift card! Click here now."
    verdict = "spam"
    reasoning = (
        "The email uses all-caps congratulations, claims a prize, "
        "and contains an urgent call-to-action link — classic spam signals."
    )
    result = grade_response(email, verdict, reasoning)
    print(f"Grade      : {result['grade']} ({grade_label(result['grade'])})")
    print(f"Explanation: {result['explanation']}")
