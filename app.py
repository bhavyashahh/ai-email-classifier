from fastapi import FastAPI
from pydantic import BaseModel
from env.environment import EmailEnv

# 1. Initialize the FastAPI web server
app = FastAPI()

# 2. Initialize your specific environment globally so it remembers the state
env = EmailEnv()

# 3. Define what the incoming action data will look like
class ActionRequest(BaseModel):
    action: str

# --- API ROUTES ---

@app.get("/")
def read_root():
    """Health check route so you know the server is running."""
    return {"status": "running", "message": "AI Email Classifier API is live!"}

@app.get("/reset")
def reset_environment():
    """
    The validator calls this to start the test.
    It triggers your env.reset() and returns the first email.
    """
    state = env.reset()
    return {"state": state}

@app.post("/step")
def step_environment(req: ActionRequest):
    """
    The validator calls this to submit the AI's action.
    It triggers your env.step() and returns the reward and next email.
    """
    next_state, reward, done, info = env.step(req.action)
    
    return {
        "state": next_state,
        "reward": reward,
        "done": done,
        "info": info
    }