from env.models import Observation, Action, Reward, EnvState
from env.tasks import TASKS
from env.reward import compute_reward


class EmailClassifierEnv:
    def __init__(self):
        self.task_id: str = ""
        self.task_data: dict = {}
        self.emails: list[dict] = []
        self.required_fields: list[str] = []
        self.step_index: int = 0
        self.done: bool = True
        self.cumulative_reward: float = 0.0
        self.history: list[dict] = []

    def get_task_ids(self) -> list[str]:
        return list(TASKS.keys())

    def reset(self, task_id: str = "task_1_easy") -> Observation:
        if task_id not in TASKS:
            raise ValueError(f"Unknown task_id: {task_id}. Available: {list(TASKS.keys())}")

        self.task_id = task_id
        self.task_data = TASKS[task_id]
        self.emails = self.task_data["emails"]
        self.required_fields = self.task_data["required_fields"]
        self.step_index = 0
        self.done = False
        self.cumulative_reward = 0.0
        self.history = []

        return self._make_observation()

    def step(self, action: dict) -> tuple[Observation | None, Reward, bool, dict]:
        if self.done:
            raise RuntimeError("Episode is done. Call reset() first.")

        email = self.emails[self.step_index]
        ground_truth = email["ground_truth"]

        reward = compute_reward(action, ground_truth, self.required_fields)
        self.cumulative_reward += reward.total

        self.history.append({
            "step": self.step_index,
            "action": action,
            "reward": reward.total,
            "feedback": reward.feedback,
        })

        self.step_index += 1
        self.done = self.step_index >= len(self.emails)

        info = {
            "step": self.step_index - 1,
            "reward_breakdown": reward.breakdown,
            "feedback": reward.feedback,
            "cumulative_reward": round(self.cumulative_reward, 3),
        }

        obs = None if self.done else self._make_observation()
        return obs, reward, self.done, info

    def state(self) -> EnvState:
        return EnvState(
            task_id=self.task_id,
            current_step=self.step_index,
            total_steps=len(self.emails) if self.emails else 0,
            done=self.done,
            cumulative_reward=round(self.cumulative_reward, 3),
            history=self.history,
        )

    def _make_observation(self) -> Observation:
        email = self.emails[self.step_index]
        return Observation(
            email_id=self.step_index,
            email_content=email["content"],
            task_id=self.task_id,
            instructions=self.task_data["instructions"],
            required_fields=self.required_fields,
            total_emails=len(self.emails),
        )
