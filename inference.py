"""
inference.py — Baseline inference script for AI Email Classifier OpenEnv.

Uses OpenAI-compatible client to run an LLM against the environment.
Emits structured [START], [STEP], [END] logs.

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
from openai import OpenAI, RateLimitError

API_BASE_URL = os.environ.get("API_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/")
MODEL_NAME = os.environ.get("MODEL_NAME", "gemini-2.5-flash")
HF_TOKEN = os.environ.get("HF_TOKEN", "")
ENV_URL = os.environ.get("ENV_URL", "http://localhost:7860")

client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)

TASKS = ["task_1_easy", "task_2_medium", "task_3_hard"]


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
        result = {}
        for field in required_fields:
            result[field] = ""
        return result


def call_llm_with_retry(email_content: str, instructions: str, required_fields: list[str], max_retries: int = 3) -> dict:
    for attempt in range(max_retries):
        try:
            return call_llm(email_content, instructions, required_fields)
        except RateLimitError as e:
            wait = 40 if attempt == 0 else 60 * (attempt + 1)
            print(f"  Rate limited, waiting {wait}s (attempt {attempt + 1}/{max_retries})...", flush=True)
            time.sleep(wait)
    return {f: "" for f in required_fields}


def run_task(task_id: str) -> dict:
    ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    print(f'[START] {{"task_id": "{task_id}", "timestamp": "{ts}"}}', flush=True)

    resp = requests.post(f"{ENV_URL}/reset", json={"task_id": task_id})
    resp.raise_for_status()
    data = resp.json()
    obs = data["observation"]

    total_reward = 0.0
    step_count = 0
    actions = []
    done = False

    while not done:
        if step_count > 0:
            time.sleep(13)
        action = call_llm_with_retry(obs["email_content"], obs["instructions"], obs["required_fields"])
        actions.append(action)

        resp = requests.post(f"{ENV_URL}/step", json={"action": action})
        resp.raise_for_status()
        result = resp.json()

        reward = result["reward"]["total"]
        done = result["done"]
        total_reward += reward

        ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        step_log = {
            "task_id": task_id,
            "step": step_count,
            "action": action,
            "reward": reward,
            "done": done,
            "timestamp": ts,
        }
        print(f"[STEP] {json.dumps(step_log)}", flush=True)

        step_count += 1
        if not done:
            obs = result["observation"]

    avg_reward = round(total_reward / step_count, 3) if step_count > 0 else 0.0
    ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    end_log = {
        "task_id": task_id,
        "total_reward": round(total_reward, 3),
        "steps": step_count,
        "avg_reward": avg_reward,
        "timestamp": ts,
    }
    print(f"[END] {json.dumps(end_log)}", flush=True)

    return end_log


def main():
    if not HF_TOKEN:
        print("ERROR: HF_TOKEN env var not set", file=sys.stderr)
        sys.exit(1)

    print(f"Environment: {ENV_URL}", flush=True)
    print(f"Model: {MODEL_NAME}", flush=True)
    print(f"API: {API_BASE_URL}", flush=True)
    print("", flush=True)

    results = {}
    for task_id in TASKS:
        result = run_task(task_id)
        results[task_id] = result
        print("", flush=True)

    print("=" * 50, flush=True)
    print("BASELINE RESULTS SUMMARY", flush=True)
    print("=" * 50, flush=True)
    for task_id, r in results.items():
        print(f"  {task_id}: avg_reward={r['avg_reward']}, steps={r['steps']}", flush=True)
    print("=" * 50, flush=True)


if __name__ == "__main__":
    main()
