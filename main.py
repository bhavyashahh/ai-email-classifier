"""
main.py
-------
Interactive email spam classifier with a built-in grader.

Workflow:
  1. User types an email in the terminal.
  2. The AI agent classifies it (spam / not spam) and gives a reasoning.
  3. The Grader evaluates the AI's response and assigns a grade (0 – 1).
  4. Everything is printed in a clear, formatted summary.
"""

from agent.geminiai_agent import get_action
from grader.grader import grade_response, grade_label


SEPARATOR = "─" * 60


def print_result(email: str, agent_result: dict, grade_result: dict) -> None:
    """Pretty-prints the full pipeline output."""
    grade = grade_result["grade"]
    label = grade_label(grade)

    print(f"\n{SEPARATOR}")
    print("  AI CLASSIFICATION REPORT")
    print(SEPARATOR)
    print(f"  Verdict   : {agent_result['verdict'].upper()}")
    print(f"  Reasoning : {agent_result['reasoning']}")
    print(SEPARATOR)
    print("  GRADER EVALUATION")
    print(SEPARATOR)
    print(f"  Grade     : {grade:.2f} / 1.00  [{label}]")
    print(f"  Feedback  : {grade_result['explanation']}")
    print(SEPARATOR)


def run_interactive() -> None:
    print("\nWelcome to the AI Email Classifier with Grader!")
    print("Type 'exit' or 'quit' to stop.\n")

    while True:
        # ── 1. Take input ──────────────────────────────────────────────
        print(SEPARATOR)
        user_email = input("Enter email content:\n> ").strip()

        if not user_email:
            print("  (empty input — please type something)\n")
            continue

        if user_email.lower() in {"exit", "quit"}:
            print("\nGoodbye!")
            break

        # ── 2. AI Agent classifies ─────────────────────────────────────
        print("\n[Agent thinking...] ", end="", flush=True)
        agent_result = get_action(user_email)
        print("done.")

        # ── 3. Grader evaluates ────────────────────────────────────────
        print("[Grader evaluating...] ", end="", flush=True)
        grade_result = grade_response(
            email=user_email,
            verdict=agent_result["verdict"],
            reasoning=agent_result["reasoning"],
        )
        print("done.")

        # ── 4. Print full summary ──────────────────────────────────────
        print_result(user_email, agent_result, grade_result)
        print()


if __name__ == "__main__":
    run_interactive()
