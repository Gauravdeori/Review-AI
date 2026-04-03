import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from rl_env import CodeReviewEnv

# Configuration
# Attempt to load from root .env or backend/.env
load_dotenv()
load_dotenv(os.path.join("backend", ".env"))

API_KEY = os.getenv("OPENAI_API_KEY")

class OpenAIAgent:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4o-mini"

    def get_action(self, code, language, difficulty):
        prompt = f"""You are an expert Code Reviewer AI. 
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

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=10,
                temperature=0,
                messages=[
                    {"role": "system", "content": "You are a precise code repair assistant. Return only the integer ID."},
                    {"role": "user", "content": prompt}
                ]
            )
            response_text = response.choices[0].message.content.strip()
            # Extract digits from response
            import re
            match = re.search(r"\d", response_text)
            if match:
                return int(match.group(0))
            return 0 # Default to NO_OP
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            return 0

def run_test():
    if not API_KEY:
        print("[WARNING] OPENAI_API_KEY not found in environment.")
        print("Please export OPENAI_API_KEY='your-key-here'")

    env = CodeReviewEnv()
    agent = OpenAIAgent(API_KEY) if API_KEY else None
    
    difficulties = ["easy", "medium", "hard"]
    all_results = []
    total_reward = 0

    print("\n" + "="*50)
    print("🔍 OPENAI GPT CODE REVIEW TEST 🔍")
    print("="*50)

    for level in difficulties:
        print(f"\n[Testing Level: {level.upper()}]")
        
        # Reset env to specific difficulty
        obs, info = env.reset(options={"difficulty": level})
        code = env.current_code
        lang = env.language
        
        print(f"Snippet:\n{code}")
        
        if agent:
            action = agent.get_action(code, lang, level)
        else:
            print("... (API Key missing, skipping OpenAI call) ...")
            action = 0 # Mock action
            
        print(f"GPT Selected Action: {action}")
        
        # Step in env
        new_obs, reward, terminated, truncated, info = env.step(action)
        total_reward += reward
        
        result = {
            "difficulty": level,
            "language": lang,
            "initial_code": code,
            "action_id": action,
            "reward": reward,
            "final_score": info.get("score"),
            "success": terminated
        }
        all_results.append(result)
        
        print(f"Step Result: Reward={reward}, Final Score={info.get('score')}/100")
        print(f"Terminated (Correct): {terminated}")

    print("\n" + "="*50)
    print(f"🎉 TEST COMPLETE! Total Accumulated Reward: {total_reward:.2f} 🎉")
    print("="*50)

    # Save to results.json
    with open("results.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=4)
    print("[*] Results saved to results.json")

if __name__ == "__main__":
    run_test()
