def interactive_goal_creation(initial_prompt: str) -> dict:
    goal = {"prompt": initial_prompt, "clarifications": []}
    while True:
        q = input("Add clarification (or empty to finish): ").strip()
        if not q:
            break
        a = input("Answer: ").strip()
        goal["clarifications"].append({"q": q, "a": a})
    return goal
