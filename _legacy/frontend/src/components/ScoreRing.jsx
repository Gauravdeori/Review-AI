/**
 * ScoreRing
 * ---------
 * Animated SVG ring that fills based on the score (0-100).
 * Color: green ≥70, yellow ≥40, red <40.
 * Shows the numeric score and an APPROVED / REJECTED badge.
 */
export default function ScoreRing({ score, verdict }) {
  const r    = 38, cx = 50, cy = 50;
  const circ = 2 * Math.PI * r;
  const fill = (score / 100) * circ;
  const color = score >= 70 ? "#4ade80" : score >= 40 ? "#facc15" : "#f87171";

  return (
    <div style={{ display: "flex", alignItems: "center", gap: 20, marginBottom: 18 }}>
      <svg width={100} height={100} style={{ transform: "rotate(-90deg)", flexShrink: 0 }}>
        <circle cx={cx} cy={cy} r={r} fill="none" stroke="#21262d" strokeWidth={7} />
        <circle
          cx={cx} cy={cy} r={r} fill="none" stroke={color} strokeWidth={7}
          strokeDasharray={`${fill} ${circ - fill}`} strokeLinecap="round"
          style={{ transition: "stroke-dasharray 0.8s ease" }}
        />
      </svg>
      <div>
        <div style={{ fontSize: 38, fontWeight: 800, color, lineHeight: 1 }}>{score}</div>
        <div style={{ fontSize: 10, color: "#6e7681", letterSpacing: 1, marginTop: 3 }}>CODE SCORE</div>
        <div style={{
          marginTop: 8, display: "inline-block",
          padding: "4px 14px", borderRadius: 20,
          fontSize: 12, fontWeight: 700, letterSpacing: 1,
          background: verdict === "APPROVED" ? "#238636" : "#da3633",
          color: "#fff",
        }}>{verdict}</div>
      </div>
    </div>
  );
}
