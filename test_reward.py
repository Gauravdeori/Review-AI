from rule_engine import rule_based_review
from sandbox import run_in_sandbox

def test_reward_system():
    env = CodeReviewEnv()
    obs, info = env.reset(options={"difficulty": "easy"})
    # Let's say we have the calculateSum snippet (JS, easy)
    # It has a missing semicolon (warning) and an off-by-one (critical)
    
    print("--- Initial State ---")
    print(f"Code:\n{env.current_code}")
    print(f"Prev Bug Counts: {env.prev_bug_counts}")

    # Action 1: Fix semicolon (ACTION_FIX_SEMICOLONS)
    obs, rew, term, trunc, info = env.step(1) # ACTION_FIX_SEMICOLONS
    print(f"\n--- After Fix Semicolon ---")
    print(f"Correct (Crit Fixed): {info['correct']}, Partial (Warn Fixed): {info['partial']}, Wrong: {info['wrong']}")
    print(f"Calculated Reward: {rew} (Expected +0.5 if 1 warning fixed)")

    # Action 2: Fix boundary (ACTION_FIX_LOOP_BOUNDARY)
    obs, rew, term, trunc, info = env.step(3) # ACTION_FIX_LOOP_BOUNDARY
    print(f"\n--- After Fix Boundary ---")
    print(f"Correct (Crit Fixed): {info['correct']}, Partial (Warn Fixed): {info['partial']}, Wrong: {info['wrong']}")
    print(f"Calculated Reward: {rew} (Expected +1.0 if 1 critical fixed)")

if __name__ == "__main__":
    from rl_env import CodeReviewEnv
    test_reward_system()

if __name__ == "__main__":
    test_reward_system()
