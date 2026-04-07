import { useState, useCallback } from "react";
import CodeEditor from "./components/CodeEditor";
import BugCard    from "./components/BugCard";
import ScoreRing  from "./components/ScoreRing";
import { LANGUAGES, DIFFICULTY_LEVELS, SAMPLE_CODE } from "./constants";

/**
 * App
 * ---
 * Root component: header controls, split-screen layout,
 * API call to /api/review, and result rendering.
 */
export default function App() {
  const [code,       setCode]       = useState(SAMPLE_CODE["JavaScript"]);
  const [language,   setLanguage]   = useState("JavaScript");
  const [difficulty, setDifficulty] = useState("medium");
  const [loading,    setLoading]    = useState(false);
  const [review,     setReview]     = useState(null);
  const [error,      setError]      = useState(null);
  const [activeTab,  setActiveTab]  = useState("bugs");
  const [source,     setSource]     = useState("");

  const highlightedLines = review?.bugs?.map((b) => b.line) || [];

  const handleLanguageChange = (lang) => {
    setLanguage(lang);
    setCode(SAMPLE_CODE[lang]);
    setReview(null);
    setError(null);
    setSource("");
  };

  // ── Call the Express backend ────────────────────────────────────────────────
  const runReview = useCallback(async () => {
    if (!code.trim()) return;
    setLoading(true);
    setReview(null);
    setError(null);
    setSource("");

    try {
      const res = await fetch("/api/review", {
        method : "POST",
        headers: { "Content-Type": "application/json" },
        body   : JSON.stringify({ code, language, difficulty }),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.error || `HTTP ${res.status}`);
      }

      const data = await res.json();
      setReview(data);
      setSource(data.source || "");
    } catch (e) {
      setError(`Review failed: ${e.message}`);
    } finally {
      setLoading(false);
    }
  }, [code, language, difficulty]);

  // ── Render ─────────────────────────────────────────────────────────────────
  return (
    <div style={{
      minHeight: "100vh", background: "#010409", color: "#e6edf3",
      fontFamily: "'DM Sans', sans-serif", display: "flex", flexDirection: "column",
    }}>
      <style>{`
        .btn { cursor:pointer; border:none; outline:none; transition:all 0.15s; }
        .btn:hover { opacity:0.85; transform:translateY(-1px); }
        .btn:active { transform:translateY(0); }
        @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }
        @keyframes slideIn { from{opacity:0;transform:translateY(6px)} to{opacity:1;transform:translateY(0)} }
      `}</style>

      {/* ── Header ── */}
      <header style={{
        borderBottom: "1px solid #21262d", padding: "12px 20px",
        display: "flex", alignItems: "center", gap: 12,
        background: "#0d1117", flexShrink: 0, flexWrap: "wrap",
      }}>
        {/* Logo */}
        <div style={{ display: "flex", alignItems: "center", gap: 10, marginRight: 8 }}>
          <div style={{
            width: 30, height: 30, borderRadius: 7,
            background: "linear-gradient(135deg,#238636,#1a7f37)",
            display: "flex", alignItems: "center", justifyContent: "center", fontSize: 15,
          }}>🔍</div>
          <div>
            <div style={{ fontWeight: 700, fontSize: 14, letterSpacing: -0.3 }}>CodeReview AI</div>
            <div style={{ fontSize: 9, color: "#6e7681", letterSpacing: 0.5 }}>POWERED BY GPT</div>
          </div>
        </div>

        <div style={{ flex: 1 }} />

        {/* Language selector */}
        <div style={{ display:"flex", gap:3, background:"#161b22", borderRadius:8, padding:3, border:"1px solid #30363d" }}>
          {LANGUAGES.map((lang) => (
            <button key={lang} className="btn" onClick={() => handleLanguageChange(lang)} style={{
              padding:"4px 11px", borderRadius:6, fontSize:11, fontWeight:600,
              background: language === lang ? "#238636" : "transparent",
              color: language === lang ? "#fff" : "#8b949e",
              fontFamily: "'JetBrains Mono', monospace",
            }}>{lang}</button>
          ))}
        </div>

        {/* Difficulty selector */}
        <div style={{ display:"flex", gap:3, background:"#161b22", borderRadius:8, padding:3, border:"1px solid #30363d" }}>
          {DIFFICULTY_LEVELS.map((d) => (
            <button key={d.id} className="btn" onClick={() => setDifficulty(d.id)} title={d.desc} style={{
              padding:"4px 11px", borderRadius:6, fontSize:11, fontWeight:600,
              background: difficulty === d.id ? `${d.color}22` : "transparent",
              color: difficulty === d.id ? d.color : "#8b949e",
              border: difficulty === d.id ? `1px solid ${d.color}44` : "1px solid transparent",
            }}>{d.label}</button>
          ))}
        </div>

        {/* Run Review */}
        <button className="btn" onClick={runReview} disabled={loading} style={{
          padding:"7px 18px", borderRadius:8,
          background: loading ? "#21262d" : "linear-gradient(135deg,#238636,#2ea043)",
          color: loading ? "#6e7681" : "#fff",
          fontSize:13, fontWeight:700, letterSpacing:0.3,
          display:"flex", alignItems:"center", gap:7,
        }}>
          {loading
            ? <><span style={{ animation:"pulse 1.2s infinite" }}>●</span> Reviewing…</>
            : <>🚀 Run Review</>}
        </button>
      </header>

      {/* ── Split body ── */}
      <div style={{ display:"flex", flex:1, overflow:"hidden", height:"calc(100vh - 57px)" }}>

        {/* LEFT — Code Editor */}
        <div style={{ flex:1, display:"flex", flexDirection:"column", borderRight:"1px solid #21262d", overflow:"hidden" }}>
          <div style={{
            padding:"7px 14px", background:"#0d1117",
            borderBottom:"1px solid #21262d",
            display:"flex", alignItems:"center", gap:8,
          }}>
            <div style={{ display:"flex", gap:5 }}>
              {["#f87171","#facc15","#4ade80"].map((c) => (
                <div key={c} style={{ width:9, height:9, borderRadius:"50%", background:c }} />
              ))}
            </div>
            <span style={{ fontFamily:"'JetBrains Mono',monospace", fontSize:11, color:"#6e7681", marginLeft:6 }}>
              {`main.${language === "Python" ? "py" : language === "C++" ? "cpp" : "js"}`}
            </span>
            {highlightedLines.length > 0 && (
              <span style={{
                marginLeft:"auto", fontSize:10, color:"#f87171",
                background:"#f8717122", padding:"2px 8px", borderRadius:4,
              }}>
                {highlightedLines.length} issue{highlightedLines.length !== 1 ? "s" : ""} flagged
              </span>
            )}
          </div>
          <div style={{ flex:1, overflow:"hidden" }}>
            <CodeEditor value={code} onChange={setCode} highlightedLines={highlightedLines} />
          </div>
        </div>

        {/* RIGHT — Feedback Panel */}
        <div style={{ width:400, display:"flex", flexDirection:"column", background:"#0d1117", overflow:"hidden", flexShrink:0 }}>

          {/* Empty state */}
          {!review && !loading && !error && (
            <div style={{ flex:1, display:"flex", flexDirection:"column", alignItems:"center", justifyContent:"center", gap:14, padding:28 }}>
              <div style={{ fontSize:44 }}>🤖</div>
              <div style={{ color:"#8b949e", textAlign:"center", lineHeight:1.7 }}>
                <div style={{ fontWeight:600, color:"#e6edf3", fontSize:15, marginBottom:6 }}>AI Review Ready</div>
                Edit the code on the left, choose a difficulty, then click{" "}
                <strong style={{ color:"#2ea043" }}>Run Review</strong>.
              </div>
              {[
                { icon:"⚠", label:"Syntax error detection" },
                { icon:"🔁", label:"Logic & off-by-one bugs" },
                { icon:"⚡", label:"Performance optimizations" },
              ].map((f) => (
                <div key={f.label} style={{
                  display:"flex", alignItems:"center", gap:10,
                  padding:"9px 14px", background:"#161b22",
                  borderRadius:8, border:"1px solid #21262d", width:"100%",
                }}>
                  <span style={{ fontSize:15 }}>{f.icon}</span>
                  <span style={{ fontSize:13, color:"#c9d1d9" }}>{f.label}</span>
                </div>
              ))}
            </div>
          )}

          {/* Loading */}
          {loading && (
            <div style={{ flex:1, display:"flex", flexDirection:"column", alignItems:"center", justifyContent:"center", gap:18 }}>
              <div style={{ fontSize:38, animation:"pulse 1.2s infinite" }}>🔍</div>
              <div style={{ color:"#8b949e", fontSize:14 }}>Analyzing your code…</div>
              <div style={{ display:"flex", gap:6 }}>
                {[0, 0.2, 0.4].map((d, i) => (
                  <div key={i} style={{ width:7, height:7, borderRadius:"50%", background:"#238636", animation:`pulse 1s ${d}s infinite` }} />
                ))}
              </div>
            </div>
          )}

          {/* Error */}
          {error && !loading && (
            <div style={{ padding:20 }}>
              <div style={{ color:"#f87171", background:"#f8717122", borderRadius:8, padding:14, fontSize:13 }}>
                ⚠ {error}
              </div>
            </div>
          )}

          {/* Results */}
          {review && !loading && (
            <div style={{ flex:1, overflow:"auto", padding:16, animation:"slideIn 0.3s ease" }}>

              {/* Source badge */}
              {(source.includes("claude") || source.includes("openai") || source.includes("gpt")) && (
                <div style={{
                  fontSize:11, color:"#4ade80", background:"#4ade8020",
                  border:"1px solid #4ade8040", borderRadius:6,
                  padding:"5px 10px", marginBottom:12, display:"flex", alignItems:"center", gap:6,
                }}>✨ OpenAI GPT analysis</div>
              )}
              {source.includes("rule") && !source.includes("openai") && !source.includes("gpt") && !source.includes("claude") && (
                <div style={{
                  fontSize:11, color:"#facc15", background:"#facc1520",
                  border:"1px solid #facc1540", borderRadius:6,
                  padding:"5px 10px", marginBottom:12, display:"flex", alignItems:"center", gap:6,
                }}>⚡ Rule-based engine</div>
              )}

              <ScoreRing score={review.score} verdict={review.verdict} />

              {/* Summary */}
              <div style={{
                background:"#161b22", border:"1px solid #30363d",
                borderRadius:8, padding:"10px 14px", marginBottom:14,
                fontSize:13, color:"#c9d1d9", lineHeight:1.6,
              }}>{review.summary}</div>

              {/* Stats row */}
              <div style={{ display:"flex", gap:8, marginBottom:14 }}>
                {[
                  { label:"Bugs",     val: review.bugs?.length || 0,                                              color:"#f87171" },
                  { label:"Opts",     val: review.optimizations?.length || 0,                                     color:"#60a5fa" },
                  { label:"Critical", val: review.bugs?.filter((b) => b.severity === "critical")?.length || 0,    color:"#f87171" },
                ].map((s) => (
                  <div key={s.label} style={{
                    flex:1, background:"#161b22", border:"1px solid #21262d",
                    borderRadius:8, padding:"8px 10px", textAlign:"center",
                  }}>
                    <div style={{ fontSize:20, fontWeight:700, color:s.color }}>{s.val}</div>
                    <div style={{ fontSize:10, color:"#6e7681", letterSpacing:0.5 }}>{s.label.toUpperCase()}</div>
                  </div>
                ))}
              </div>

              {/* Tabs */}
              <div style={{ display:"flex", gap:3, marginBottom:12, background:"#161b22", borderRadius:8, padding:3 }}>
                {["bugs","optimizations","patch"].map((t) => (
                  <button key={t} className="btn" onClick={() => setActiveTab(t)} style={{
                    flex:1, padding:"5px 0", borderRadius:6, fontSize:11,
                    fontWeight:600, letterSpacing:0.5, textTransform:"uppercase",
                    background: activeTab === t ? "#21262d" : "transparent",
                    color: activeTab === t ? "#e6edf3" : "#8b949e",
                  }}>{t}</button>
                ))}
              </div>

              {/* Bugs tab */}
              {activeTab === "bugs" && (
                <div>
                  {!review.bugs?.length
                    ? <div style={{ textAlign:"center", color:"#4ade80", padding:24, fontSize:14 }}>✅ No bugs detected!</div>
                    : review.bugs.map((bug, i) => <BugCard key={bug.id} bug={bug} index={i} />)
                  }
                </div>
              )}

              {/* Optimizations tab */}
              {activeTab === "optimizations" && (
                <div>
                  {!review.optimizations?.length
                    ? <div style={{ textAlign:"center", color:"#8b949e", padding:24, fontSize:14 }}>No optimizations suggested.</div>
                    : review.optimizations.map((opt) => (
                        <div key={opt.id} style={{
                          background:"#161b22",
                          border:`1px solid ${opt.impact === "high" ? "#60a5fa44" : "#21262d"}`,
                          borderLeft:`3px solid ${opt.impact === "high" ? "#60a5fa" : opt.impact === "medium" ? "#7dd3fc" : "#93c5fd"}`,
                          borderRadius:8, padding:"10px 14px", marginBottom:10,
                        }}>
                          <div style={{ marginBottom:6 }}>
                            <span style={{
                              fontSize:10, fontWeight:700, padding:"2px 6px", borderRadius:4,
                              letterSpacing:1, textTransform:"uppercase",
                              background:"#1f6feb22", color:"#60a5fa",
                            }}>{opt.impact} impact</span>
                          </div>
                          <div style={{ fontSize:13, color:"#c9d1d9" }}>⚡ {opt.description}</div>
                        </div>
                      ))
                  }
                </div>
              )}

              {/* Patch tab */}
              {activeTab === "patch" && (
                <div>
                  <div style={{ fontSize:12, color:"#8b949e", marginBottom:8 }}>
                    Corrected snippet for the most critical issue:
                  </div>
                  <div style={{
                    background:"#0d1117", borderRadius:8, padding:14,
                    fontFamily:"'JetBrains Mono',monospace", fontSize:12,
                    color:"#7ee787", border:"1px solid #238636",
                    whiteSpace:"pre-wrap", lineHeight:1.6,
                  }}>{review.codePatch || "No patch available."}</div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
