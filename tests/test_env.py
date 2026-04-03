import pytest
import numpy as np
import gymnasium as gym
from rl_env import CodeReviewEnv

@pytest.fixture
def env():
    return CodeReviewEnv()

def test_env_reset(env):
    """Verify that reset() returns valid observation and info."""
    obs, info = env.reset()
    
    # 1. Check observation shape and type
    assert isinstance(obs, np.ndarray)
    assert obs.shape == (10,)
    assert obs.dtype == np.float32
    
    # 2. Check info dict
    assert isinstance(info, dict)
    assert "score" in info
    assert "bugs" in info

def test_env_step(env):
    """Verify that step() returns correctly typed results."""
    env.reset()
    action = env.action_space.sample() # Pick a random discrete action
    
    obs, reward, terminated, truncated, info = env.step(action)
    
    # 1. Verify observation
    assert isinstance(obs, np.ndarray)
    assert obs.shape == (10,)
    
    # 2. Verify reward is a float
    assert isinstance(reward, float)
    
    # 3. Verify terminal flags
    assert isinstance(terminated, bool)
    assert isinstance(truncated, bool)
    
    # 4. Verify info
    assert isinstance(info, dict)
    assert "score" in info

def test_env_episodes_limit(env):
    """Verify the environment can be run for multiple steps without crashing."""
    env.reset()
    for _ in range(5):
        action = env.action_space.sample()
        obs, reward, terminated, truncated, info = env.step(action)
        if terminated or truncated:
            break
    assert True # If we reach here without crash, it passes
