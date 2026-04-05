def compute_reward(action , correct_answer):
    action = action.lower()
    correct_answer = correct_answer.lower()

    if correct_answer in action:
        return 1.0
    return 0.0