import re

def rule_based_review(code: str, language: str, difficulty: str) -> dict:
    """
    rule_engine.py — Python Rules-Based Code Review Engine
    A direct port of the Node.js rule-based engine to avoid IPC/HTTP overhead
    during synchronous Reinforcement Learning environments.
    """
    lines = code.split("\n")
    bugs = []
    bug_id = 1
    
    for idx, line in enumerate(lines):
        ln = idx + 1
        t = line.strip()
        if not t:
            continue
            
        # ── SYNTAX (all difficulties) ─────────────────────────────────────────
        if language in ["JavaScript", "C++"]:
            is_block_line = (
                t.endswith("{") or t.endswith("}") or t.endswith(",") or
                t.endswith(";") or t.endswith(":") or t.startswith("//") or
                t.startswith("*") or t.startswith("#") or
                re.match(r"^(for|if|while|else|function|class|return)\b", t) or
                "=>" in t or re.match(r"^[{}]", t)
            )

            if not is_block_line and len(t) > 2:
                bugs.append({
                    "id": f"bug_{bug_id}", "line": ln, "severity": "warning", "type": "syntax",
                    "description": "Possible missing semicolon at end of statement.",
                    "fix": f"Add a semicolon → `{t};`",
                })
                bug_id += 1

        # Mismatched parentheses
        opens = t.count("(")
        closes = t.count(")")
        if opens != closes and not t.startswith("//") and not t.startswith("#"):
            bugs.append({
                "id": f"bug_{bug_id}", "line": ln, "severity": "critical", "type": "syntax",
                "description": f"Mismatched parentheses — {opens} open vs {closes} close.",
                "fix": "Balance the opening and closing parentheses on this line.",
            })
            bug_id += 1

        if difficulty == "easy":
            continue

        # ── LOGIC (medium+) ───────────────────────────────────────────────────

        # Off-by-one: i <= arr.length  or  i <= n
        if re.search(r"i\s*<=\s*(arr\.length|n\b)", t):
            bugs.append({
                "id": f"bug_{bug_id}", "line": ln, "severity": "critical", "type": "logic",
                "description": "Off-by-one error: `<=` with array length causes out-of-bounds access on the last iteration.",
                "fix": "Change `<=` to `<` in the loop condition.",
            })
            bug_id += 1

        # Python range with float division: range(len(s) / 2)
        if language == "Python" and re.search(r"range\s*\(.*\/\s*\d", t):
            bugs.append({
                "id": f"bug_{bug_id}", "line": ln, "severity": "critical", "type": "syntax",
                "description": "Python 3: `/` produces a float; `range()` requires an integer.",
                "fix": "Use integer division `//` → e.g. `range(len(s) // 2)`.",
            })
            bug_id += 1

        # Wrong palindrome index: s[len(s) - i] → should be s[len(s) - 1 - i]
        if re.search(r"\w\s*\[\s*len\s*\(\w+\)\s*-\s*\w+\s*\]", t) and "- 1" not in t:
            bugs.append({
                "id": f"bug_{bug_id}", "line": ln, "severity": "critical", "type": "logic",
                "description": "Wrong reverse index: `s[len(s) - i]` is off by one — should be `s[len(s) - 1 - i]`.",
                "fix": "Use `s[len(s) - 1 - i]` for correct mirrored indexing.",
            })
            bug_id += 1

        # max initialised to 0 (wrong for all-negative arrays)
        if re.search(r"\bmax\w*\s*=\s*0\b", t) and not t.startswith("//") and not t.startswith("#"):
            fix_str = "Use `float('-inf')` or initialise to `arr[0]`." if language == "Python" else "Use `INT_MIN` or initialise to `arr[0]`."
            bugs.append({
                "id": f"bug_{bug_id}", "line": ln, "severity": "warning", "type": "logic",
                "description": "max initialised to 0 — returns incorrect result when all values are negative.",
                "fix": fix_str,
            })
            bug_id += 1

        if difficulty == "medium":
            continue

        # ── PERFORMANCE (hard) ────────────────────────────────────────────────

        # Nested loops over same array → O(n²)
        if re.search(r"for\s*\(.*i\s*<\s*(arr\.length|n\b)", t) or re.search(r"for\s+\w+\s+in\s+range", t):
            next_few = " ".join(lines[idx + 1: idx + 6])
            if re.search(r"for\s*\(.*j\s*<\s*(arr\.length|n\b)", next_few) or re.search(r"for\s+\w+\s+in\s+range", next_few):
                bugs.append({
                    "id": f"bug_{bug_id}", "line": ln, "severity": "info", "type": "performance",
                    "description": "Nested loops over the same collection → O(n²) time complexity.",
                    "fix": "Use a Set/HashSet/dict for O(n) duplicate or lookup operations.",
                })
                bug_id += 1

    # Deduplicate by line + type
    seen = set()
    deduped = []
    for b in bugs:
        key = f"{b['line']}-{b['type']}"
        if key not in seen:
            seen.add(key)
            deduped.append(b)

    # Score
    critical_count = len([b for b in deduped if b["severity"] == "critical"])
    warning_count = len([b for b in deduped if b["severity"] == "warning"])
    info_count = len([b for b in deduped if b["severity"] == "info"])
    
    score = max(0, 100 - (critical_count * 20) - (warning_count * 10) - (info_count * 5))

    # Optimizations (hard only)
    optimizations = []
    if difficulty == "hard":
        optimizations = [
            {"id": "opt_1", "description": "Replace nested-loop duplicate detection with a Set for O(n) time.", "impact": "high"},
            {"id": "opt_2", "description": "Use built-in reduce / Math.max instead of manual loops for clarity and speed.", "impact": "medium"},
            {"id": "opt_3", "description": "Consider early-return patterns to avoid unnecessary iterations.", "impact": "low"},
        ]

    top_critical = next((b for b in deduped if b["severity"] == "critical"), None)
    code_patch = f"// Line {top_critical['line']} — fix:\n// {top_critical['fix']}" if top_critical else "// No critical bugs detected."

    summary = "No issues detected — code looks clean." if not deduped else f"Found {len(deduped)} issue(s): {critical_count} critical, {warning_count} warnings."

    return {
        "verdict": "APPROVED" if score >= 70 else "REJECTED",
        "score": score,
        "summary": summary,
        "bugs": deduped,
        "optimizations": optimizations,
        "codePatch": code_patch,
        "source": "python-rule-based-local"
    }
