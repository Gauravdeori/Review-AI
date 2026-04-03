import os
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from rl_env import CodeReviewEnv

# 1. Create the reinforcement learning environment
print("[*] Initializing Gymnasium CodeReview Environment...")
env = make_vec_env(lambda: CodeReviewEnv(), n_envs=1)

# 2. Define the PPO model with MlpPolicy
# Hyperparameters: 3e-4 learning rate, 2048 n_steps
model = PPO(
    "MlpPolicy", 
    env, 
    verbose=1, 
    learning_rate=3e-4, 
    n_steps=2048,
    tensorboard_log="./tb_logs/"
)

# 3. Train the agent
print("[*] Commencing training loop [100,000 steps]...")
model.learn(total_timesteps=100000)

# 4. Save the trained weight matrix
model_name = "codereview_ppo_agent"
model.save(model_name)
print(f"[*] Training finished! Model saved as {model_name}.zip")
