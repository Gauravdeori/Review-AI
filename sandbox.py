import subprocess
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path

@dataclass
class SandboxResult:
    compiled: bool
    tests_passed: bool
    timed_out: bool
    reward_bonus: float
    stderr: str

HIDDEN_TESTS_DIR = Path(os.path.dirname(__file__)) / "tests" / "hidden"

def run_in_sandbox(code: str, language: str) -> SandboxResult:
    """Run code in isolated Docker sandbox and return evaluation metrics."""
    
    # 1. Prepare temp directory locally on host
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # 2. Setup testing framework contexts based on language
        if language == "Python":
            filename = "eval_test.py"
            test_file = HIDDEN_TESTS_DIR / "python" / "test_suite.py"
            docker_image = "cr-sandbox-python"
            cmd = ["pytest", "/sandbox/code/eval_test.py", "--disable-warnings", "-q"]
            
        elif language == "JavaScript":
            filename = "eval.test.js"
            test_file = HIDDEN_TESTS_DIR / "javascript" / "test_suite.js"
            docker_image = "cr-sandbox-node"
            cmd = ["jest", "/sandbox/code/eval.test.js", "--passWithNoTests"]
        else:
            return SandboxResult(False, False, False, 0.0, "Unsupported language")

        # 3. Concatenate Agent Code + Hidden Tests Locally
        eval_script_path = temp_path / filename
        hidden_test_code = ""
        if test_file.exists():
            with open(test_file, "r", encoding="utf-8") as f:
                hidden_test_code = f.read()
                
        with open(eval_script_path, "w", encoding="utf-8") as f:
            f.write(code)
            f.write("\n\n")
            f.write(hidden_test_code)

        # 4. Construct strictly isolated Docker command
        docker_cmd = [
            "docker", "run", "--rm",
            "--network", "none",
            "--memory", "256m",
            "--cpus", "1.0",
            "-v", f"{str(temp_path.absolute())}:/sandbox/code:ro",
            docker_image
        ] + cmd

        compiled = False
        tests_passed = False
        timed_out = False
        stderr_log = ""
        exit_code = 127
        
        try:
            # 5. Execute with 5 second hard timeout limit
            proc = subprocess.run(
                docker_cmd,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            # 6. Parse Test Execution Exit Codes
            exit_code = proc.returncode
            stderr_log = proc.stderr.strip()
            stdout_log = proc.stdout.strip()
            
            # Common Docker system errors
            is_docker_err = any(x in stderr_log.lower() for x in ["daemon", "not found", "no such image", "connection refused"])
            
            if exit_code == 0:
                compiled = True
                tests_passed = True
            elif exit_code == 1 and not is_docker_err:
                # Tests failed, but syntax compiled/interpreted perfectly fine
                compiled = True
                tests_passed = False
            else:
                # exit code > 1 or docker error implies deep crash, Docker missing, syntax exception, etc.
                compiled = False
                tests_passed = False

        except subprocess.TimeoutExpired:
            timed_out = True
            
        except FileNotFoundError:
            # Docker is likely not installed on host.
            stderr_log = "Docker executable not found on path."
            compiled = False
            tests_passed = False
            
        # 7. Calculate Second-Stage Reward Matrix
        reward = 0.0
        if timed_out:
            reward = -5.0
        elif not compiled:
            reward = -10.0 # Significant penalty for environment or syntax crash
        elif tests_passed:
            reward = 60.0 # +10 compile + 50 tests strictly passed = 60
        else:
            reward = 10.0 # Just syntax OK without crashing, but logical tests failed
            
        # 8. Log Execution Trace for debugging
        try:
            with open("sandbox_execution.log", "a", encoding="utf-8") as log:
                log.write(f"Lang: {language} | Compiled: {compiled} | Tests: {tests_passed} | TimeOut: {timed_out} | Reward: {reward}\n")
                if stderr_log:
                    log.write(f"ERRORS:\n{stderr_log}\n")
        except Exception:
            pass
                
        return SandboxResult(
            compiled=compiled,
            tests_passed=tests_passed,
            timed_out=timed_out,
            reward_bonus=reward,
            stderr=stderr_log
        )
