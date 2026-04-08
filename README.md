# AI Email Classifier — OpenEnv Environment

A real-world OpenEnv environment that simulates **email triage** — the task of classifying incoming emails by spam status, category, and priority level. This is a task knowledge workers perform daily, making it a practical benchmark for evaluating AI agent capabilities.

## Motivation

Email triage is one of the most universal productivity tasks. An effective agent must understand context, detect deception (spam/phishing), categorize by topic, and assess urgency — skills that transfer to many real-world applications.

## Action Space

JSON object with the following fields (which fields are required depends on the task):

| Field | Type | Values |
|-------|------|--------|
| `spam_status` | string | `spam`, `not_spam` |
| `category` | string | `work`, `personal`, `promotions`, `updates`, `finance` |
| `priority` | string | `high`, `medium`, `low` |

## Observation Space

| Field | Type | Description |
|-------|------|-------------|
| `email_id` | int | Index of current email |
| `email_content` | string | Raw email text |
| `task_id` | string | Current task identifier |
| `instructions` | string | What the agent should do |
| `required_fields` | list[str] | Which fields to provide |
| `total_emails` | int | Total emails in this task |

## Tasks

### Task 1: Spam Detection (Easy)
Classify 5 obvious emails as spam or not_spam. Clear-cut cases with strong signals.

### Task 2: Spam + Category (Medium)
Classify 5 emails by spam status AND category. Requires understanding email content and context.

### Task 3: Full Triage (Hard)
Classify 5 ambiguous emails by spam status, category, AND priority. Includes phishing disguised as legitimate email, edge cases, and nuanced priority assessment.

## Reward Design

- **Partial credit**: Each required field is weighted and scored independently
- **Field weights** scale with task complexity (e.g., Task 1: spam=100%, Task 3: spam=34%, category=33%, priority=33%)
- **Partial matches**: Adjacent priority levels (e.g., medium vs high) and related categories earn 0.4 credit
- **Score range**: 0.0 to 1.0 per step, averaged across the episode

## Setup

### Docker (recommended)
```bash
docker build -t email-classifier .
docker run -p 7860:7860 email-classifier
```

### Local
```bash
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 7860
```

### Run Inference
```bash
export API_BASE_URL="https://generativelanguage.googleapis.com/v1beta/openai/"
export MODEL_NAME="gemini-2.5-flash"
export HF_TOKEN="your-api-key"
export ENV_URL="http://localhost:7860"
python inference.py
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/reset` | POST | Reset env with `{"task_id": "task_1_easy"}` |
| `/step` | POST | Submit action `{"action": {...}}` |
| `/state` | GET | Get current environment state |
| `/tasks` | GET | List available task IDs |
| `/grade` | POST | Grade a full set of actions for a task |

## Baseline Scores

| Task | Difficulty | Avg Reward |
|------|-----------|------------|
| task_1_easy | Easy | ~0.95+ |
| task_2_medium | Medium | ~0.85+ |
| task_3_hard | Hard | ~0.70+ |

*Scores from Gemini 2.5 Flash baseline.*
