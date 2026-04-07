import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

client = genai.Client()

SYSTEM_INSTRUCTION = """You are an advanced email analysis system. Perform the following 3 tasks on the given email content and provide a brief justification for each decision:

1) Spam vs Not Spam: Answer strictly 'Spam' or 'Not Spam'.
2) Smart Category: Categorize as 'Work', 'Personal', 'Promotions', 'Updates', or 'Finance'.
3) Priority: Rate the priority as 'High', 'Medium', or 'Low'.

Format your response exactly like this:

Task 1 - Spam Status: [Result]
Justification: [Brief explanation of why you chose this status]

Task 2 - Category: [Result]
Justification: [Brief explanation of why you chose this category]

Task 3 - Priority: [Result]
Justification: [Brief explanation of why you chose this priority]"""


def get_email_analysis(email_content: str) -> dict:
    """
    Runs the 3-task email analysis and returns a structured dict.

    Returns:
        {
          "spam_status":            "Spam" | "Not Spam",
          "spam_justification":     str,
          "category":               "Work" | "Personal" | "Promotions" | "Updates" | "Finance",
          "category_justification": str,
          "priority":               "High" | "Medium" | "Low",
          "priority_justification": str,
          "raw":                    str  (full raw model output)
        }
    """
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=email_content,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.2,
        ),
    )

    raw = response.text.strip()
    result = {
        "spam_status": "unknown",
        "spam_justification": "",
        "category": "unknown",
        "category_justification": "",
        "priority": "unknown",
        "priority_justification": "",
        "raw": raw,
    }

    current_task = None
    for line in [l.strip() for l in raw.splitlines() if l.strip()]:
        upper = line.upper()

        if upper.startswith("TASK 1"):
            colon = line.find(":")
            if colon != -1:
                result["spam_status"] = line[colon + 1:].strip()
            current_task = "spam"

        elif upper.startswith("TASK 2"):
            colon = line.find(":")
            if colon != -1:
                result["category"] = line[colon + 1:].strip()
            current_task = "category"

        elif upper.startswith("TASK 3"):
            colon = line.find(":")
            if colon != -1:
                result["priority"] = line[colon + 1:].strip()
            current_task = "priority"

        elif upper.startswith("JUSTIFICATION:"):
            text = line.split(":", 1)[1].strip()
            if current_task == "spam":
                result["spam_justification"] = text
            elif current_task == "category":
                result["category_justification"] = text
            elif current_task == "priority":
                result["priority_justification"] = text

    return result


# --- Optional: Local Testing ---
if __name__ == "__main__":
    test_email = "Hi team, review the Q3 report attached and approve by EOD Friday. Urgent."
    r = get_email_analysis(test_email)
    print(f"Spam     : {r['spam_status']}  — {r['spam_justification']}")
    print(f"Category : {r['category']}  — {r['category_justification']}")
    print(f"Priority : {r['priority']}  — {r['priority_justification']}")
