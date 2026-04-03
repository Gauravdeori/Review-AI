import os
from stable_baselines3 import PPO
from rl_env import CodeReviewEnv

def evaluate():
    # 1. Load the trained model
    model_path = "codereview_ppo_agent"
    if not os.path.exists(model_path + ".zip"):
        print(f"[ERROR] Model file {model_path}.zip not found! Please run train.py first.")
        return

    print("[*] Loading PPO CodeReview Model...")
    model = PPO.load(model_path)
    
    # 2. Setup Evaluation Environment
    env = CodeReviewEnv()
    num_episodes = 10
    
    print("\n" + "="*50)
    print(f"🚀 COMMENCING EVALUATION: {num_episodes} EPISODES 🚀")
    print("="*50)

    total_rewards = []
    
    for i in range(num_episodes):
        obs, info = env.reset()
        done = False
        steps = 0
        ep_reward = 0
        
        while not done and steps < 10: # Limit steps to avoid infinite loop
            steps += 1
            action, _states = model.predict(obs, deterministic=True)
            obs, reward, terminated, truncated, info = env.step(action)
            ep_reward += reward
            done = terminated or truncated
            
        total_rewards.append(ep_reward)
        print(f"\n[Episode {i+1}] Finished!")
        print(f"=> Final Score: {info.get('score', 0)}/100")
        print(f"=> Sandbox Result: {'SUCCESS' if info.get('sandbox_passed') else 'FAILED'}")
        print(f"=> Steps Taken: {steps}")
        print(f"=> Cumulative Reward: {ep_reward:.2f}")

    avg_rew = sum(total_rewards) / len(total_rewards)
    print("\n" + "="*50)
    print(f"🎉 FINAL EVALUATION COMPLETE! Avg Reward: {avg_rew:.2f} 🎉")
    print("="*50 + "\n")

if __name__ == "__main__":
    evaluate()
