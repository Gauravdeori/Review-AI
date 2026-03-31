# 🏆 Hackathon Judges' Guide: Code-Review AI + RL

This document provides everything you need to evaluate the **Code-Review App** and its **Gymnasium RL Environment**.

## 🎯 The Innovation
This project bridges the gap between **Static Analysis** and **Autonomous AI**. It features:
1.  **A Modern Web UI**: Built with React/Node.js, allowing humans to get instant feedback on their code.
2.  **A Deterministic Rule Engine**: A high-performance Python-native port for scoring code without LLM latency.
3.  **An RL Environment**: A Gymnasium wrapper (`rl_env.py`) that uses a **Multi-Stage Reward System**: 
    - **Stage 1 (Rules)**: Static analysis for syntax and logic.
    - **Stage 2 (Execution)**: Running code in an isolated **Docker Sandbox** against hidden unit tests.

---

## 🛠️ Option A: The Web Interface (Visual/Human mode)
To see the application UI as a human user:
1.  Open the folder in your terminal.
2.  Run the following command:
    ```bash
    python host_preview.py
    ```
3.  **Chrome will open** to `http://localhost:8080/preview_app.html`. 
4.  You can type JavaScript or Python code on the left and see the **Visual Ring Score** and **Bug Cards** on the right.

---

## 🤖 Option B: The RL Agent (AI/Autonomous mode)
To see how an AI agent is trained to "fix" code autonomously using Reinforcement Learning:
1.  Ensure you have `gymnasium` and `numpy` installed.
2.  Run the specialized visual demo:
    ```bash
    python demo_agent.py
    ```
3.  **What you will see**: The script will reset to a buggy state, simulate an agent "deciding" on character-level edits, and show the **Real-Time Reward Signals** (+10 for syntax, +50 for test pass) as the agent optimizes the code.

---

## 🛡️ The Security Sandbox (Docker)
The project includes a `sandbox.py` that executes code inside `cr-sandbox-python` and `cr-sandbox-node` containers. 
- **Security**: `--network none`, `--read-only`, and strict resource limits (256MB RAM).
- **Execution**: If Docker is not available on your system, the project **gracefully degrades** (it will still work using the Rule Engine but will penalize "crashes" by -5.0).

---

## 🚀 Key Files for Evaluation
- `rl_env.py`: The core Gymnasium Environment (Matrix Math/Observation/Action).
- `rule_engine.py`: The deterministic scoring engine (Ported from JS to Python).
- `sandbox.py`: The Docker-based execution layer.
- `demo_agent.py`: The easiest way to see the agent flow in a few seconds!

---

**Thank you for evaluating our project! 🚀**
