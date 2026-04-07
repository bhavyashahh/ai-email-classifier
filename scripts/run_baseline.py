from env.environment import EmailEnv
from grader.grader import grade
from agent.geminiai_agent import get_action

def run():
    env = EmailEnv()
    state = env.reset()

    done = False
    total_reward = 0
    steps = 0

    while not done:
        action = get_action(state)
        print(f"Email: {state}")
        print(f"AI Action: {action}\n")

        state, reward, done, _ = env.step(action)
        total_reward += reward
        steps += 1

    final_score = grade(total_reward , steps)
    print("Final Score: ",final_score)


if __name__ == "__main__":
    run()