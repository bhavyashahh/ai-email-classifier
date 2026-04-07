"""
main.py
-------
Interactive email analysis system with a 3-task grader.

Workflow per iteration:
  1. User types email content.
  2. AI agent returns: spam verdict, category, priority — each with justification.
  3. Grader evaluates all three tasks and returns per-task grades + weighted overall.
  4. A clean terminal report is printed.
"""

from agent.geminiai_agent import get_email_analysis
from grader.grader import grade_response, grade_label

SEP  = "─" * 62
SEP2 = "· · " * 15


def bar(grade: float, width: int = 20) -> str:
    """Renders a simple ASCII progress bar for a grade."""
    filled = round(grade * width)
    return "[" + "█" * filled + "░" * (width - filled) + f"]  {grade:.2f}"


def print_report(email: str, agent: dict, grade: dict) -> None:
    overall = grade["overall_grade"]
    label   = grade_label(overall)

    print(f"\n{SEP}")
    print("  AI ANALYSIS REPORT")
    print(SEP)

    # Task 1
    print(f"  Task 1 — Spam status   : {agent['spam_status']}")
    print(f"  Justification          : {agent['spam_justification']}")
    print(f"  Grade                  : {bar(grade['task1_grade'])}  (weight 50%)")
    print(f"  Grader note            : {grade['task1_explanation']}")
    print()

    # Task 2
    print(f"  Task 2 — Category      : {agent['category']}")
    print(f"  Justification          : {agent['category_justification']}")
    print(f"  Grade                  : {bar(grade['task2_grade'])}  (weight 30%)")
    print(f"  Grader note            : {grade['task2_explanation']}")
    print()

    # Task 3
    print(f"  Task 3 — Priority      : {agent['priority']}")
    print(f"  Justification          : {agent['priority_justification']}")
    print(f"  Grade                  : {bar(grade['task3_grade'])}  (weight 20%)")
    print(f"  Grader note            : {grade['task3_explanation']}")

    # Overall
    print(f"\n{SEP}")
    print(f"  OVERALL GRADE          : {bar(overall, 30)}  [{label}]")
    print(f"  Formula                : 0.50×T1 + 0.30×T2 + 0.20×T3")
    print(SEP)


def run_interactive() -> None:
    print("\nWelcome to the AI Email Analyser with Grader!")
    print("Type 'exit' or 'quit' to stop.\n")

    while True:
        print(SEP)
        raw_input = input("Paste email content:\n> ").strip()

        if not raw_input:
            print("  (empty — please type something)\n")
            continue

        if raw_input.lower() in {"exit", "quit"}:
            print("\nGoodbye!")
            break

        # ── Agent ──────────────────────────────────────────────────────
        print("\n[Agent analysing...] ", end="", flush=True)
        agent_result = get_email_analysis(raw_input)
        print("done.")

        # ── Grader ─────────────────────────────────────────────────────
        print("[Grader evaluating...] ", end="", flush=True)
        grade_result = grade_response(raw_input, agent_result)
        print("done.")

        # ── Report ─────────────────────────────────────────────────────
        print_report(raw_input, agent_result, grade_result)
        print()


if __name__ == "__main__":
    run_interactive()
