import gymnasium as gym
from gymnasium import spaces
import random
import numpy as np
import re
from rule_engine import rule_based_review
from sandbox import run_in_sandbox

# --- Action Constants ---
ACTION_NOOP = 0
ACTION_FIX_SEMICOLONS = 1
ACTION_FIX_PARENTHESES = 2
ACTION_FIX_LOOP_BOUNDARY = 3
ACTION_FIX_PYTHON_DIVISION = 4
ACTION_FIX_INDEXING = 5

class CodeReviewEnv(gym.Env):
    """
    Overhauled Gymnasium Environment for CodeReview AI.
    Uses discrete high-level actions and feature-based observations.
    """
    metadata = {"render_modes": ["ansi"]}

    def __init__(self):
        super().__init__()
        
        # Observation Space: 10-feature vector
        # [Semicolons, Parens, Boundary, FloatDiv, Indexing, Max0, On2, Score, LangID, DiffID]
        self.observation_space = spaces.Box(low=0, high=100, shape=(10,), dtype=np.float32)
        
        # Action Space: 6 discrete 'Smart Fix' operations
        self.action_space = spaces.Discrete(6)
        
        self.current_code = ""
        self.current_score = 0
        self.language = "JavaScript"
        self.difficulty = "medium"
        self.total_episodes = 0
        
        # 5 Diverse Buggy Snippets
        self.buggy_snippets = [
            {
                "code": "function calculateSum(arr) {\n  let total = 0\n  for (let i = 0; i <= arr.length; i++) {\n    total += arr[i]\n  }\n  return total\n}",
                "lang": "JavaScript", "diff": "easy"
            },
            {
                "code": "def is_palindrome(s):\n    for i in range(len(s) / 2):\n        if s[i] != s[len(s) - i]:\n            return False\n    return True",
                "lang": "Python", "diff": "medium"
            },
            {
                "code": "function findDuplicate(arr) {\n  for (let i = 0; i < arr.length; i++) {\n    for (let j = 0; j < arr.length; j++) {\n      if (arr[i] === arr[j]) return true\n    }\n  }\n  return false\n}",
                "lang": "JavaScript", "diff": "hard"
            },
            {
                "code": "def find_max(arr):\n    max_val = 0\n    for x in arr:\n        if x > max_val:\n            max_val = x\n    return max_val",
                "lang": "Python", "diff": "medium"
            },
            {
                "code": "function checkBalance(a, b) {\n  let res = (a + b\n  return res % 2 === 0\n}",
                "lang": "JavaScript", "diff": "easy"
            }
        ]

    def encode_observation(self, code: str, review_info: dict) -> np.ndarray:
        """Extracts 10 numerical features from the code and rule engine output."""
        bugs = review_info.get("bugs", [])
        
        # Feature counts
        semicolon_cnt = sum(1 for b in bugs if "semicolon" in b["description"].lower())
        paren_cnt     = sum(1 for b in bugs if "parentheses" in b["description"].lower())
        boundary_cnt  = sum(1 for b in bugs if "off-by-one" in b["description"].lower())
        float_div_cnt = sum(1 for b in bugs if "float" in b["description"].lower())
        indexing_cnt  = sum(1 for b in bugs if "reverse index" in b["description"].lower())
        max0_cnt      = sum(1 for b in bugs if "max initialised to 0" in b["description"].lower())
        on2_cnt       = sum(1 for b in bugs if "o(n2)" in b["description"].lower())
        
        score_norm = review_info.get("score", 0)
        lang_id = 0 if self.language == "JavaScript" else 1
        diff_id = 0 if self.difficulty == "easy" else (1 if self.difficulty == "medium" else 2)
        
        features = np.array([
            semicolon_cnt, paren_cnt, boundary_cnt, float_div_cnt, indexing_cnt, 
            max0_cnt, on2_cnt, score_norm, lang_id, diff_id
        ], dtype=np.float32)
        
        return features

    def decode_action(self, action_id: int, code: str) -> str:
        """Applies high-level fixes to the code string based on the discrete action."""
        lines = code.split("\n")
        new_lines = []
        
        for line in lines:
            t = line.strip()
            if not t:
                new_lines.append(line)
                continue
                
            filtered_line = line
            
            if action_id == ACTION_FIX_SEMICOLONS:
                # Add semicolon if missing and not a block/comment
                if self.language in ["JavaScript", "C++"]:
                    if not (t.endswith("{") or t.endswith("}") or t.endswith(";") or t.endswith(":") or "//" in t or "function" in t or "for" in t or "if" in t):
                        filtered_line = line.rstrip() + ";"
            
            elif action_id == ACTION_FIX_PARENTHESES:
                # Simple balancing for the demo: ensure ( and ) match
                opens = filtered_line.count("(")
                closes = filtered_line.count(")")
                if opens > closes:
                    filtered_line = filtered_line + (")" * (opens - closes))
                elif closes > opens:
                    # very aggressive fix for mismatched close
                    filtered_line = ("(" * (closes - opens)) + filtered_line
            
            elif action_id == ACTION_FIX_LOOP_BOUNDARY:
                # Fix <= length
                filtered_line = re.sub(r"i\s*<=\s*(arr\.length|n\b)", "i < \\1", filtered_line)
                
            elif action_id == ACTION_FIX_PYTHON_DIVISION:
                # Fix float division in range
                filtered_line = re.sub(r"range\s*\((.*?)\/\s*(\d+)\)", "range(\\1 // \\2)", filtered_line)
                
            elif action_id == ACTION_FIX_INDEXING:
                # Fix len(s) - i -> len(s) - 1 - i
                filtered_line = re.search(r"(\w+)\s*\[\s*len\s*\(\w+\)\s*-\s*(\w+)\s*\]", filtered_line)
                if filtered_line and "- 1" not in line:
                    filtered_line = line.replace(f"- {filtered_line.group(2)}", f"- 1 - {filtered_line.group(2)}")
                else:
                    filtered_line = line
            
            new_lines.append(filtered_line)
            
        return "\n".join(new_lines)

    def get_bug_counts(self, bugs):
        """Helper to count bugs by severity."""
        counts = {"critical": 0, "warning": 0, "info": 0}
        for b in bugs:
            counts[b.get("severity", "info")] = counts.get(b.get("severity", "info"), 0) + 1
        return counts

    def reset(self, *, seed=None, options=None):
        """Curriculum management: Samples snippets based on total episodes played or manual override."""
        super().reset(seed=seed, options=options)
        self.total_episodes += 1
        
        # Check for manual difficulty override in options
        manual_difficulty = options.get("difficulty") if options else None
        
        if manual_difficulty:
            allowed = [s for s in self.buggy_snippets if s["diff"] == manual_difficulty]
            if not allowed: # Fallback
                allowed = self.buggy_snippets
        else:
            # Simple Curriculum: Graduating every 100 episodes
            if self.total_episodes < 200:
                allowed = [s for s in self.buggy_snippets if s["diff"] == "easy"]
            elif self.total_episodes < 500:
                allowed = [s for s in self.buggy_snippets if s["diff"] in ["easy", "medium"]]
            else:
                allowed = self.buggy_snippets
            
        snippet = random.choice(allowed)
        self.current_code = snippet["code"]
        self.language = snippet["lang"]
        self.difficulty = snippet["diff"]
        
        # Initial evaluation
        info = rule_based_review(self.current_code, self.language, self.difficulty)
        self.current_score = info.get("score", 0)
        self.prev_bug_counts = self.get_bug_counts(info.get("bugs", []))
        
        return self.encode_observation(self.current_code, info), info

    def step(self, action: int):
        """Applies reward shaping and sandbox verification."""
        # Translate discrete action to string edit
        new_code = self.decode_action(action, self.current_code)
        
        # Evaluate with Rule Engine
        review = rule_based_review(new_code, self.language, self.difficulty)
        new_score = review.get("score", 0)
        new_bug_counts = self.get_bug_counts(review.get("bugs", []))
        
        # --- Synchronized Reward System ---
        # 1. Correct findings: Critical bugs removed
        correct_count = max(0, self.prev_bug_counts["critical"] - new_bug_counts["critical"])
        
        # 2. Partial findings: Warning/Info bugs removed
        prev_others = self.prev_bug_counts["warning"] + self.prev_bug_counts["info"]
        new_others = new_bug_counts["warning"] + new_bug_counts["info"]
        partial_count = max(0, prev_others - new_others)
        
        # 3. Wrong findings: Bugs added or score stayed same/dropped
        added_count = sum(max(0, new_bug_counts[k] - self.prev_bug_counts[k]) for k in new_bug_counts)
        wrong_count = added_count if (added_count > 0 or new_score <= self.current_score) else 0
        if correct_count == 0 and partial_count == 0 and wrong_count == 0:
            wrong_count = 1 # Force penalty for no-op if no improvement
            
        # Calculate Reward based on image formula
        reward = (correct_count * 1.0) + (partial_count * 0.5) - (wrong_count * 0.2)
        
        # Execute sandbox for metadata
        sandbox_res = run_in_sandbox(new_code, self.language)
        
        self.current_code = new_code
        self.current_score = new_score
        self.prev_bug_counts = new_bug_counts
        
        # Terminate if score is 100 or tests passed
        terminated = sandbox_res.tests_passed or (new_score == 100)
        
        # Additional info for logging
        info = {
            "score": new_score,
            "correct": correct_count,
            "partial": partial_count,
            "wrong": wrong_count,
            "reward_total": reward,
            "sandbox_passed": sandbox_res.tests_passed,
            "lang": self.language
        }
        
        obs = self.encode_observation(self.current_code, review)
        return obs, reward, terminated, False, info

if __name__ == "__main__":
    env = CodeReviewEnv()
    obs, info = env.reset()
    print(f"Initial Obs: {obs}")
    print(f"Initial Code:\n{env.current_code}")
    
    # Simulate fixing a JS sum (Action 1 followed by Action 3)
    new_obs, rew, term, trunc, info = env.step(ACTION_FIX_SEMICOLONS)
    print(f"\nAfter Fix Semicolons -> Reward: {rew}, Score: {info['score']}")
    print(f"Code:\n{env.current_code}")
    
    new_obs, rew, term, trunc, info = env.step(ACTION_FIX_LOOP_BOUNDARY)
    print(f"\nAfter Fix Boundary -> Reward: {rew}, Score: {info['score']}")
    print(f"Final Code:\n{env.current_code}")
    print(f"Terminated: {term}")
