import { useRef } from "react";

/**
 * CodeEditor
 * ----------
 * A textarea with a synchronized line-number gutter.
 * Lines listed in `highlightedLines` are shown in red with a ● marker.
 */
export default function CodeEditor({ value, onChange, highlightedLines = [] }) {
  const taRef     = useRef(null);
  const gutterRef = useRef(null);
  const lines     = (value || "").split("\n");

  const syncScroll = () => {
    if (gutterRef.current && taRef.current)
      gutterRef.current.scrollTop = taRef.current.scrollTop;
  };

  return (
    <div style={{ display: "flex", height: "100%", fontFamily: "'JetBrains Mono', monospace", fontSize: 13 }}>
      {/* Gutter */}
      <div
        ref={gutterRef}
        style={{
          width: 44, background: "#0d1117", color: "#3d444d",
          padding: "12px 0", overflowY: "hidden", userSelect: "none",
          borderRight: "1px solid #21262d", flexShrink: 0,
        }}
      >
        {lines.map((_, i) => {
          const ln    = i + 1;
          const isHit = highlightedLines.includes(ln);
          return (
            <div key={i} style={{
              height: 19.5, lineHeight: "19.5px", textAlign: "right",
              paddingRight: 8, fontSize: 11,
              color     : isHit ? "#f87171" : "#3d444d",
              background: isHit ? "rgba(248,113,113,0.1)" : "transparent",
            }}>
              {isHit ? "●" : ln}
            </div>
          );
        })}
      </div>

      {/* Textarea */}
      <textarea
        ref={taRef}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onScroll={syncScroll}
        spellCheck={false}
        style={{
          flex: 1, background: "#0d1117", color: "#e6edf3",
          border: "none", outline: "none", resize: "none",
          padding: "12px 16px", lineHeight: "19.5px",
          fontFamily: "inherit", fontSize: 13, caretColor: "#58a6ff",
        }}
      />
    </div>
  );
}
