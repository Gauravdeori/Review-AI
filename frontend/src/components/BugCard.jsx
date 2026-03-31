import { useState } from "react";
import { severityColor, typeIcon } from "../constants";

/**
 * BugCard
 * -------
 * Expandable card showing a single bug: severity, type, line number,
 * description, and the suggested fix.
 */
export default function BugCard({ bug, index }) {
  const [open, setOpen] = useState(index === 0);

  return (
    <div style={{
      background: "#161b22",
      border: `1px solid ${severityColor(bug.severity)}33`,
      borderRadius: 8, marginBottom: 10, overflow: "hidden",
    }}>
      {/* Header row */}
      <div
        onClick={() => setOpen(!open)}
        style={{
          display: "flex", alignItems: "center", gap: 10,
          padding: "10px 14px", cursor: "pointer",
          borderLeft: `3px solid ${severityColor(bug.severity)}`,
        }}
      >
        <span style={{ fontSize: 15 }}>{typeIcon(bug.type)}</span>
        <div style={{ flex: 1 }}>
          <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
            <span style={{
              fontSize: 10, fontWeight: 700, letterSpacing: 1,
              padding: "2px 6px", borderRadius: 4, textTransform: "uppercase",
              background: `${severityColor(bug.severity)}22`,
              color: severityColor(bug.severity),
            }}>{bug.severity}</span>
            <span style={{ fontSize: 11, color: "#8b949e" }}>Line {bug.line}</span>
            <span style={{ fontSize: 11, color: "#6e7681", textTransform: "uppercase", letterSpacing: 0.5 }}>{bug.type}</span>
          </div>
          <div style={{ color: "#c9d1d9", fontSize: 13, marginTop: 3 }}>{bug.description}</div>
        </div>
        <span style={{ color: "#484f58", fontSize: 11 }}>{open ? "▲" : "▼"}</span>
      </div>

      {/* Expanded fix */}
      {open && (
        <div style={{ padding: "0 14px 12px 14px", borderTop: "1px solid #21262d" }}>
          <div style={{ marginTop: 10, fontSize: 12, color: "#8b949e", marginBottom: 6 }}>💡 Suggested Fix</div>
          <div style={{
            background: "#0d1117", borderRadius: 6, padding: "10px 12px",
            fontFamily: "'JetBrains Mono', monospace", fontSize: 12,
            color: "#7ee787", borderLeft: "3px solid #238636",
            whiteSpace: "pre-wrap",
          }}>{bug.fix}</div>
        </div>
      )}
    </div>
  );
}
