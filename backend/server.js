/**
 * server.js — AI Code Review Backend
 * -----------------------------------
 * Express server that exposes a single POST /api/review endpoint.
 * It forwards code to the Anthropic Claude API and returns a
 * structured JSON review (bugs, optimizations, verdict, score).
 *
 * Fallback: if ANTHROPIC_API_KEY is missing, the rule-based engine
 * (reviewEngine.js) is used instead so the app still works offline.
 */

require("dotenv").config();
const express = require("express");
const cors    = require("cors");
const Anthropic = require("@anthropic-ai/sdk");
const { ruleBasedReview } = require("./reviewEngine");

const app  = express();
const PORT = process.env.PORT || 4000;

// ── Middleware ────────────────────────────────────────────────────────────────
app.use(cors());               // allow requests from the React dev server
app.use(express.json());

// ── Anthropic client (only created when key is present) ──────────────────────
const anthropic = process.env.ANTHROPIC_API_KEY
  ? new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY })
  : null;

// ── System prompt sent to Claude ─────────────────────────────────────────────
const SYSTEM_PROMPT = `You are an expert code reviewer AI. Analyze the submitted code and return ONLY a valid JSON object — no markdown fences, no preamble, nothing else.

JSON schema:
{
  "verdict": "APPROVED" or "REJECTED",
  "score": number from 0 to 100,
  "summary": "one concise sentence describing overall code quality",
  "bugs": [
    {
      "id": "bug_1",
      "line": integer line number,
      "severity": "critical" | "warning" | "info",
      "type": "syntax" | "logic" | "performance" | "style",
      "description": "clear description of the bug",
      "fix": "concrete fix suggestion"
    }
  ],
  "optimizations": [
    {
      "id": "opt_1",
      "description": "optimization suggestion",
      "impact": "high" | "medium" | "low"
    }
  ],
  "codePatch": "corrected snippet for the most critical bug"
}

Scoring: start at 100. Deduct 20 per critical bug, 10 per warning, 5 per info. Approve if score >= 70.

Difficulty levels:
- easy:   syntax errors only (semicolons, brackets, parentheses)
- medium: syntax + logical bugs (off-by-one, wrong conditions, infinite loops)
- hard:   all above + performance improvements (complexity, redundant loops, better data structures)`;

// ── POST /api/review ──────────────────────────────────────────────────────────
app.post("/api/review", async (req, res) => {
  const { code, language, difficulty } = req.body;

  // Basic validation
  if (!code || typeof code !== "string" || !code.trim()) {
    return res.status(400).json({ error: "code is required" });
  }
  if (!["JavaScript", "Python", "C++"].includes(language)) {
    return res.status(400).json({ error: "language must be JavaScript, Python, or C++" });
  }
  if (!["easy", "medium", "hard"].includes(difficulty)) {
    return res.status(400).json({ error: "difficulty must be easy, medium, or hard" });
  }

  // ── No API key → rule-based fallback ───────────────────────────────────────
  if (!anthropic) {
    console.log("[review] No API key — using rule-based engine");
    const result = ruleBasedReview(code, language, difficulty);
    return res.json({ ...result, source: "rule-based" });
  }

  // ── Claude API ─────────────────────────────────────────────────────────────
  try {
    console.log(`[review] ${language} / ${difficulty} — calling Claude`);

    const message = await anthropic.messages.create({
      model      : "claude-3-5-sonnet-latest",
      max_tokens : 1500,
      system     : SYSTEM_PROMPT,
      messages   : [
        {
          role   : "user",
          content: `Review this ${language} code at difficulty level: ${difficulty}\n\nCode:\n\`\`\`${language.toLowerCase()}\n${code}\n\`\`\``,
        },
      ],
    });

    const raw   = message.content.map((c) => c.text || "").join("");
    const clean = raw.replace(/```json|```/g, "").trim();
    const parsed = JSON.parse(clean);

    return res.json({ ...parsed, source: "claude-ai" });
  } catch (err) {
    console.error("[review] Claude API error:", err.message);

    // Graceful fallback on API failure
    const fallback = ruleBasedReview(code, language, difficulty);
    return res.json({ ...fallback, source: "rule-based-fallback", apiError: err.message });
  }
});

// ── GET /api/health ───────────────────────────────────────────────────────────
app.get("/api/health", (_req, res) => {
  res.json({
    status : "ok",
    aiReady: !!anthropic,
    model  : "claude-3-5-sonnet-latest",
  });
});

// ── Start ─────────────────────────────────────────────────────────────────────
app.listen(PORT, () => {
  console.log(`✅ Code Review API running on http://localhost:${PORT}`);
  console.log(`   AI engine: ${anthropic ? "Claude (Anthropic)" : "Rule-based fallback"}`);
});
