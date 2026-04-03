"""
server/app.py — Standalone OpenEnv-compatible deployment server.
Serves the RL environment REST API + code review web UI.
Used for HuggingFace Spaces deployment.
"""

import os
import sys
import json

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI
from rl_env import CodeReviewEnv
from rule_engine import rule_based_review

# Load environment
load_dotenv()
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "backend", ".env"))

API_KEY = os.getenv("OPENAI_API_KEY")
PORT = int(os.getenv("PORT", 7860))

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), ".."))
CORS(app)

ai_client = OpenAI(api_key=API_KEY) if API_KEY else None
env_instance = CodeReviewEnv()

SYSTEM_PROMPT = """You are an expert code reviewer AI. Analyze the code and return ONLY a valid JSON object.
JSON schema:
{
  "verdict": "APPROVED" | "REJECTED",
  "score": number 0-100,
  "summary": "string",
  "bugs": [{"id": "b1", "line": 1, "severity": "critical", "type": "logic", "description": "...", "fix": "..."}],
  "optimizations": [{"id": "o1", "description": "...", "impact": "high"}],
  "codePatch": "string"
}"""

# ── Static files ───────────────────────────────────────────────────────────────
@app.route("/")
def serve_index():
    return send_from_directory(app.static_folder, "index.html")

# ── Code Review API ────────────────────────────────────────────────────────────
@app.route("/api/review", methods=["POST"])
def review_code():
    data = request.json
    code = data.get("code", "")
    lang = data.get("language", "JavaScript")
    diff = data.get("difficulty", "medium")

    if not ai_client:
        return jsonify({**rule_based_review(code, lang, diff), "source": "python-rule-based"})

    try:
        response = ai_client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=1500,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Review this {lang} code (Difficulty: {diff}):\n\n{code}"}
            ]
        )
        raw = response.choices[0].message.content
        clean = raw.replace("```json", "").replace("```", "").strip()
        parsed = json.loads(clean)
        return jsonify({**parsed, "source": "python-openai"})
    except Exception as e:
        return jsonify({**rule_based_review(code, lang, diff), "source": "python-rule-based-fallback", "error": str(e)})

# ── OpenEnv Endpoints ──────────────────────────────────────────────────────────
@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "environment": "codereview-ai",
        "ai_ready": ai_client is not None,
        "model": "gpt-4o-mini"
    })

@app.route("/reset", methods=["POST"])
def reset_env():
    data = request.json or {}
    options = {}
    if "difficulty" in data:
        options["difficulty"] = data["difficulty"]
    
    obs, info = env_instance.reset(options=options if options else None)
    return jsonify({
        "observation": {"features": obs.tolist()},
        "info": {
            "score": info.get("score", 0),
            "code": env_instance.current_code,
            "language": env_instance.language,
            "difficulty": env_instance.difficulty,
        }
    })

@app.route("/step", methods=["POST"])
def step_env():
    data = request.json or {}
    action = data.get("action", 0)
    
    obs, reward, terminated, truncated, info = env_instance.step(action)
    return jsonify({
        "observation": {"features": obs.tolist()},
        "reward": float(reward),
        "terminated": bool(terminated),
        "truncated": bool(truncated),
        "info": {
            "score": info.get("score", 0),
            "sandbox_passed": info.get("sandbox_passed", False),
            "code": env_instance.current_code,
            "language": env_instance.language,
        }
    })

@app.route("/state", methods=["GET"])
def get_state():
    return jsonify({
        "code": env_instance.current_code,
        "language": env_instance.language,
        "difficulty": env_instance.difficulty,
        "score": env_instance.current_score,
    })

if __name__ == "__main__":
    print(f"✅ CodeReview AI Server on http://0.0.0.0:{PORT}")
    print(f"   AI engine: {'OpenAI (GPT-4o-mini)' if ai_client else 'Rule-based fallback'}")
    app.run(host="0.0.0.0", port=PORT, debug=False)
