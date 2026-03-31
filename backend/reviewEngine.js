/**
 * reviewEngine.js — Rule-Based Code Review Engine
 * -------------------------------------------------
 * A deterministic, zero-dependency engine that analyzes code
 * without any LLM API. Used as a fallback when ANTHROPIC_API_KEY
 * is not set, or when the Claude API call fails.
 *
 * Covers:
 *   easy   → syntax: missing semicolons, mismatched parentheses
 *   medium → logic:  off-by-one loops, wrong index, bad max init, Python int division
 *   hard   → perf:  nested O(n²) loops, redundant checks
 */

"use strict";

/**
 * @param {string} code
 * @param {"JavaScript"|"Python"|"C++"} language
 * @param {"easy"|"medium"|"hard"} difficulty
 * @returns {object} review result matching the Claude JSON schema
 */
function ruleBasedReview(code, language, difficulty) {
  const lines = code.split("\n");
  const bugs  = [];
  let   id    = 1;

  lines.forEach((line, idx) => {
    const ln = idx + 1;
    const t  = line.trim();
    if (!t) return;

    // ── SYNTAX (all difficulties) ─────────────────────────────────────────
    if (language === "JavaScript" || language === "C++") {
      const isBlockLine =
        t.endsWith("{") || t.endsWith("}") || t.endsWith(",") ||
        t.endsWith(";") || t.endsWith(":") || t.startsWith("//") || 
        t.startsWith("*") || t.startsWith("#") || 
        /^(for|if|while|else|function|class|return)\b/.test(t) ||
        t.includes("=>") || /^[{}]/.test(t);

      if (!isBlockLine && t.length > 2) {
        bugs.push({
          id: `bug_${id++}`, line: ln, severity: "warning", type: "syntax",
          description: "Possible missing semicolon at end of statement.",
          fix: `Add a semicolon → \`${t};\``,
        });
      }
    }

    // Mismatched parentheses
    const opens  = (t.match(/\(/g) || []).length;
    const closes = (t.match(/\)/g) || []).length;
    if (opens !== closes && !t.startsWith("//") && !t.startsWith("#")) {
      bugs.push({
        id: `bug_${id++}`, line: ln, severity: "critical", type: "syntax",
        description: `Mismatched parentheses — ${opens} open vs ${closes} close.`,
        fix: "Balance the opening and closing parentheses on this line.",
      });
    }

    if (difficulty === "easy") return;

    // ── LOGIC (medium+) ───────────────────────────────────────────────────

    // Off-by-one: i <= arr.length  or  i <= n
    if (/i\s*<=\s*(arr\.length|n\b)/.test(t)) {
      bugs.push({
        id: `bug_${id++}`, line: ln, severity: "critical", type: "logic",
        description: "Off-by-one error: `<=` with array length causes out-of-bounds access on the last iteration.",
        fix: "Change `<=` to `<` in the loop condition.",
      });
    }

    // Python range with float division: range(len(s) / 2)
    if (language === "Python" && /range\s*\(.*\/\s*\d/.test(t)) {
      bugs.push({
        id: `bug_${id++}`, line: ln, severity: "critical", type: "syntax",
        description: "Python 3: `/` produces a float; `range()` requires an integer.",
        fix: "Use integer division `//` → e.g. `range(len(s) // 2)`.",
      });
    }

    // Wrong palindrome index: s[len(s) - i] → should be s[len(s) - 1 - i]
    if (/\w\s*\[\s*len\s*\(\w+\)\s*-\s*\w+\s*\]/.test(t) && !t.includes("- 1")) {
      bugs.push({
        id: `bug_${id++}`, line: ln, severity: "critical", type: "logic",
        description: "Wrong reverse index: `s[len(s) - i]` is off by one — should be `s[len(s) - 1 - i]`.",
        fix: "Use `s[len(s) - 1 - i]` for correct mirrored indexing.",
      });
    }

    // max initialised to 0 (wrong for all-negative arrays)
    if (/\bmax\w*\s*=\s*0\b/.test(t) && !t.startsWith("//") && !t.startsWith("#")) {
      bugs.push({
        id: `bug_${id++}`, line: ln, severity: "warning", type: "logic",
        description: "max initialised to 0 — returns incorrect result when all values are negative.",
        fix: language === "Python"
          ? "Use `float('-inf')` or initialise to `arr[0]`."
          : "Use `INT_MIN` or initialise to `arr[0]`.",
      });
    }

    if (difficulty === "medium") return;

    // ── PERFORMANCE (hard) ────────────────────────────────────────────────

    // Nested loops over same array → O(n²)
    if (/for\s*\(.*i\s*<\s*(arr\.length|n\b)/.test(t) || /for\s+\w+\s+in\s+range/.test(t)) {
      const nextFew = lines.slice(idx + 1, idx + 6).join(" ");
      if (/for\s*\(.*j\s*<\s*(arr\.length|n\b)/.test(nextFew) || /for\s+\w+\s+in\s+range/.test(nextFew)) {
        bugs.push({
          id: `bug_${id++}`, line: ln, severity: "info", type: "performance",
          description: "Nested loops over the same collection → O(n²) time complexity.",
          fix: "Use a Set/HashSet/dict for O(n) duplicate or lookup operations.",
        });
      }
    }
  });

  // Deduplicate by line + type
  const seen    = new Set();
  const deduped = bugs.filter((b) => {
    const key = `${b.line}-${b.type}`;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });

  // Score
  const score = Math.max(
    0,
    100
      - deduped.filter((b) => b.severity === "critical").length * 20
      - deduped.filter((b) => b.severity === "warning").length  * 10
      - deduped.filter((b) => b.severity === "info").length     *  5,
  );

  // Optimizations (hard only)
  const optimizations = difficulty === "hard" ? [
    { id: "opt_1", description: "Replace nested-loop duplicate detection with a Set for O(n) time.", impact: "high" },
    { id: "opt_2", description: "Use built-in reduce / Math.max instead of manual loops for clarity and speed.", impact: "medium" },
    { id: "opt_3", description: "Consider early-return patterns to avoid unnecessary iterations.", impact: "low" },
  ] : [];

  const topCritical = deduped.find((b) => b.severity === "critical");
  const codePatch   = topCritical
    ? `// Line ${topCritical.line} — fix:\n// ${topCritical.fix}`
    : "// No critical bugs detected.";

  return {
    verdict        : score >= 70 ? "APPROVED" : "REJECTED",
    score,
    summary        : deduped.length === 0
      ? "No issues detected — code looks clean."
      : `Found ${deduped.length} issue(s): ${deduped.filter((b) => b.severity === "critical").length} critical, ${deduped.filter((b) => b.severity === "warning").length} warnings.`,
    bugs           : deduped,
    optimizations,
    codePatch,
  };
}

module.exports = { ruleBasedReview };
