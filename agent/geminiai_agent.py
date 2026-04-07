import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

client = genai.Client()

SYSTEM_PROMPT = """You are a spam classifier. Analyze the given email and respond in this EXACT format:

VERDICT: spam  OR  VERDICT: not spam

REASONING: <explain in 2-3 sentences why you classified it this way. Be specific — mention the exact words, phrases, sender patterns, or structural signals that led to your decision.>

Do not add anything else. Follow the format strictly."""


def get_action(state: str) -> dict:
    """
    Classifies an email as spam or not spam.

    Returns a dict with keys:
        - verdict  : "spam" or "not spam"
        - reasoning: the AI's justification string
        - raw      : the full raw response text (for debugging)
    """
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=state,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT
        ),
    )

    raw = response.text.strip()
    verdict = "unknown"
    reasoning = ""

    for line in raw.splitlines():
        line = line.strip()
        if line.upper().startswith("VERDICT:"):
            verdict = line.split(":", 1)[1].strip().lower()
        elif line.upper().startswith("REASONING:"):
            reasoning = line.split(":", 1)[1].strip()

    return {
        "verdict": verdict,
        "reasoning": reasoning,
        "raw": raw,
    }


# --- Optional: Local Testing ---
if __name__ == "__main__":
    test_message = "CONGRATULATIONS! You've won a $1000 gift card! Click here now."
    result = get_action(test_message)
    print("Verdict  :", result["verdict"])
    print("Reasoning:", result["reasoning"])
