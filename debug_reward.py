from rl_env import CodeReviewEnv
from rule_engine import rule_based_review

env = CodeReviewEnv()
# Manually set code
env.current_code = "function test() {\n  let a = 1\n  return a\n}"
env.language = "JavaScript"
env.difficulty = "easy"
info = rule_based_review(env.current_code, env.language, env.difficulty)
env.prev_bug_counts = env.get_bug_counts(info.get("bugs", []))
print(f"Initial Bugs: {env.prev_bug_counts}")

# Step with fix semicolons (1)
obs, rew, term, trunc, info = env.step(1)
print(f"New Code:\n{env.current_code}")
print(f"Reward: {rew}")
print(f"Info: {info}")
