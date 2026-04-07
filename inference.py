"""
Inference Script Example adapted for CodeReviewEnv
"""

import os
import re
import textwrap
from typing import List, Optional

from dotenv import load_dotenv
from openai import OpenAI
from rl_env import CodeReviewEnv

load_dotenv()
load_dotenv(os.path.join("server", ".env"))
load_dotenv(os.path.join("..", ".env"))

API_KEY = os.getenv("OPENAI_API_KEY") or os.getenv("API_KEY") or os.getenv("HF_TOKEN")

# Allow easy config through env vars
API_BASE_URL = os.getenv("API_BASE_URL") or "https://api.openai.com/v1"
MODEL_NAME = os.getenv("MODEL_NAME") or "gpt-4o-mini"
TASK_NAME = os.getenv("MY_ENV_V4_TASK", "codereview")
BENCHMARK = os.getenv("MY_ENV_V4_BENCHMARK", "CodeReviewEnv")
MAX_STEPS = 8
TEMPERATURE = 0.0
MAX_TOKENS = 10
SUCCESS_SCORE_THRESHOLD = 100.0

def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    print(
        f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error_val}",
        flush=True,
    )

def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}", flush=True)

def build_user_prompt(code: str, language: str, difficulty: str) -> str:
    return textwrap.dedent(
        f"""You are an expert Code Reviewer AI. 
Analyze the following {language} code snippet ({difficulty} difficulty) and identify the bug.
Then, select the best repair action from the following list:

0: NO_OP (No changes needed)
1: FIX_SEMICOLONS (Add missing semicolons in JavaScript/C++)
2: FIX_PARENTHESES (Balance mismatched parentheses)
3: FIX_LOOP_BOUNDARY (Change <= to < in array length loops)
4: FIX_PYTHON_DIVISION (Change / to // in Python range() functions)
5: FIX_INDEXING (Change [len(s)-i] to [len(s)-1-i] for reverse indexing)

CODE:
{code}

Return ONLY the action ID (0, 1, 2, 3, 4, or 5). Do not provide any explanation."""
    ).strip()

def get_action(client: OpenAI, code: str, language: str, difficulty: str) -> int:
    user_prompt = build_user_prompt(code, language, difficulty)
    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a precise code repair assistant. Return only the integer ID."},
                {"role": "user", "content": user_prompt},
            ],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            stream=False,
        )
        response_text = (completion.choices[0].message.content or "").strip()
        match = re.search(r"\d", response_text)
        if match:
            return int(match.group(0))
        return 0
    except Exception as exc:
        print(f"[DEBUG] Model request failed: {exc}", flush=True)
        return 0

def main() -> None:
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    env = CodeReviewEnv()

    rewards: List[float] = []
    steps_taken = 0
    score = 0.0
    success = False

    log_start(task=TASK_NAME, env=BENCHMARK, model=MODEL_NAME)

    try:
        # Reset the environment (picks a random snippet unless manual config via options)
        obs, info = env.reset(options={"difficulty": "medium"}) 
        
        for step in range(1, MAX_STEPS + 1):
            code = env.current_code
            lang = env.language
            difficulty = env.difficulty
            
            action_id = get_action(client, code, lang, difficulty)

            obs_out, reward, terminated, truncated, step_info = env.step(action_id)
            
            rewards.append(reward)
            steps_taken = step
            error = None 
            
            action_desc = f"action_{action_id}"
            
            log_step(step=step, action=action_desc, reward=reward, done=terminated, error=error)

            if terminated:
                break

        score = step_info.get("score", 0.0)
        # Normalize score to [0, 1] for the metrics
        normalized_score = min(max(score / 100.0, 0.0), 1.0)
        success = step_info.get("sandbox_passed", False) or (score == 100.0)
        
        log_end(success=success, steps=steps_taken, score=normalized_score, rewards=rewards)

    except Exception as e:
        print(f"[DEBUG] Execution error: {e}", flush=True)
        log_end(success=False, steps=steps_taken, score=0.0, rewards=rewards)
    finally:
        env.close()

if __name__ == "__main__":
    main()
