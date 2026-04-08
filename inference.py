"""
inference.py — Baseline inference script for AI Email Classifier OpenEnv.

Uses OpenAI-compatible client to run an LLM against the environment.
Emits structured [START], [STEP], [END] logs per the mandatory format.

Required env vars:
  API_BASE_URL  - LLM API endpoint
  MODEL_NAME    - Model identifier
  HF_TOKEN      - API key
"""

import os
import sys
import json
import time
import requests
from typing import List, Optional
from openai import OpenAI, RateLimitError

API_BASE_URL = os.getenv("API_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/")
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-2.5-flash")
HF_TOKEN = os.getenv("HF_TOKEN") or os.getenv("API_KEY", "")
ENV_URL = os.getenv("ENV_URL", "http://localhost:7860")
BENCHMARK = "ai-email-classifier"

TASKS = ["task_1_easy", "task_2_medium", "task_3_hard"]


client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)


# ── Logging helpers (mandatory format) ──────────────────────────────

def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    done_val = str(done).lower()
    error_val = error if error else "null"
    print(f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error_val}", flush=True)


def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.2f} rewards={rewards_str}", flush=True)


# ── LLM call ────────────────────────────────────────────────────────

def call_llm(email_content: str, instructions: str, required_fields: list[str]) -> dict:
    fields_str = ", ".join(required_fields)
    system_prompt = f"""You are an email classification agent. {instructions}

You must respond with ONLY a valid JSON object containing these fields: {fields_str}

Valid values:
- spam_status: "spam" or "not_spam"
- category: "work", "personal", "promotions", "updates", or "finance"
- priority: "high", "medium", or "low"

Respond with ONLY the JSON object, no other text."""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Classify this email:\n\n{email_content}"},
        ],
        temperature=0.0,
    )

    text = response.choices[0].message.content.strip()
    text = text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {f: "" for f in required_fields}


def call_llm_with_retry(email_content: str, instructions: str, required_fields: list[str], max_retries: int = 3) -> dict:
    for attempt in range(max_retries):
        try:
            return call_llm(email_content, instructions, required_fields)
        except RateLimitError:
            wait = 40 if attempt == 0 else 60 * (attempt + 1)
            print(f"  Rate limited, waiting {wait}s (attempt {attempt + 1}/{max_retries})...", flush=True)
            time.sleep(wait)
    return {f: "" for f in required_fields}


# ── Run one task ────────────────────────────────────────────────────

def run_task(task_id: str) -> dict:
    log_start(task=task_id, env=BENCHMARK, model=MODEL_NAME)

    resp = requests.post(f"{ENV_URL}/reset", json={"task_id": task_id})
    resp.raise_for_status()
    obs = resp.json()["observation"]

    rewards: List[float] = []
    steps_taken = 0
    done = False
    last_error = None

    try:
        while not done:
            if steps_taken > 0:
                time.sleep(13)

            action = call_llm_with_retry(obs["email_content"], obs["instructions"], obs["required_fields"])
            action_str = json.dumps(action, separators=(",", ":"))

            resp = requests.post(f"{ENV_URL}/step", json={"action": action})
            resp.raise_for_status()
            result = resp.json()

            reward = result["reward"]["total"]
            done = result["done"]
            rewards.append(reward)
            steps_taken += 1

            log_step(step=steps_taken, action=action_str, reward=reward, done=done, error=None)

            if not done:
                obs = result["observation"]

    except Exception as exc:
        last_error = str(exc)
        print(f"[DEBUG] Error during task {task_id}: {last_error}", flush=True)

    score = sum(rewards) / len(rewards) if rewards else 0.0
    score = min(max(score, 0.0), 1.0)
    success = score >= 0.5

    log_end(success=success, steps=steps_taken, score=score, rewards=rewards)

    return {"task_id": task_id, "score": score, "steps": steps_taken, "success": success}


# ── Main ────────────────────────────────────────────────────────────

def main():
    if not HF_TOKEN:
        print("ERROR: HF_TOKEN env var not set", file=sys.stderr)
        sys.exit(1)

    results = {}
    for task_id in TASKS:
        result = run_task(task_id)
        results[task_id] = result

    print("", flush=True)
    print("=" * 50, flush=True)
    print("BASELINE RESULTS SUMMARY", flush=True)
    print("=" * 50, flush=True)
    for task_id, r in results.items():
        print(f"  {task_id}: score={r['score']:.2f}, steps={r['steps']}, success={r['success']}", flush=True)
    print("=" * 50, flush=True)


if __name__ == "__main__":
    main()
