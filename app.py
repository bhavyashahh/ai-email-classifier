from fastapi import FastAPI, Query
from pydantic import BaseModel
from env.environment import EmailClassifierEnv
from grader.grader import grade_task

app = FastAPI(title="AI Email Classifier - OpenEnv")
env = EmailClassifierEnv()


class ActionRequest(BaseModel):
    action: dict


class ResetRequest(BaseModel):
    task_id: str = "task_1_easy"


@app.get("/")
def health():
    return {"status": "running", "env": "ai-email-classifier"}


@app.post("/reset")
def reset(req: ResetRequest = ResetRequest()):
    obs = env.reset(req.task_id)
    return {"observation": obs.model_dump()}


@app.post("/step")
def step(req: ActionRequest):
    obs, reward, done, info = env.step(req.action)
    return {
        "observation": obs.model_dump() if obs else None,
        "reward": reward.model_dump(),
        "done": done,
        "info": info,
    }


@app.get("/state")
def state():
    return env.state().model_dump()


@app.get("/tasks")
def list_tasks():
    return {"tasks": env.get_task_ids()}


@app.post("/grade")
def grade(task_id: str = Query(...), actions: list[dict] = []):
    return grade_task(task_id, actions)
