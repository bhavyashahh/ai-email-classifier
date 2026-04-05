from env.tasks import easy_tasks
from env.reward import compute_reward

class EmailEnv:
    def __init__(self):
        self.tasks = easy_tasks
        self.index = 0

    def reset(self):
        self.index = 0
        return self.tasks[self.index]["email"]
    
    def step(self , action):
        task = self.tasks[self.index]
        correct = task.get("label" , "")

        reward = compute_reward(action , correct)

        self.index += 1
        done = self.index >= len(self.tasks)

        if not done:
            next_state = self.tasks[self.index]["email"]
        else:
            next_state = None

        return next_state, reward, done, {}
    