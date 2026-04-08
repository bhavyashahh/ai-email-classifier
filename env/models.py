from pydantic import BaseModel, Field


class Observation(BaseModel):
    email_id: int = Field(description="Index of current email in the task")
    email_content: str = Field(description="Raw email text to classify")
    task_id: str = Field(description="Current task identifier")
    instructions: str = Field(description="What the agent should do")
    required_fields: list[str] = Field(description="Fields the agent must provide")
    total_emails: int = Field(description="Total emails in this task")


class Action(BaseModel):
    spam_status: str = Field(default="", description="spam or not_spam")
    category: str = Field(default="", description="work/personal/promotions/updates/finance")
    priority: str = Field(default="", description="high/medium/low")


class Reward(BaseModel):
    total: float = Field(ge=0.0, le=1.0, description="Overall reward for this step")
    breakdown: dict[str, float] = Field(default_factory=dict)
    feedback: str = Field(default="")


class EnvState(BaseModel):
    task_id: str
    current_step: int
    total_steps: int
    done: bool
    cumulative_reward: float
    history: list[dict] = Field(default_factory=list)
