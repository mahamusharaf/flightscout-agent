import { useState } from "react";

const EXAMPLES = [
  "Cheap JFK to LAX, Aug 15, don't care about layovers",
  "Business class London to Tokyo, comfort over price",
  "Lahore to Dubai in two weeks, budget $400",
];

export default function SearchForm({ onSearch, isLoading }) {
  const [query, setQuery] = useState("");

  function handleSubmit(e) {
    e.preventDefault();
    const q = query.trim();
    if (!q || isLoading) return;
    onSearch(q);
  }

  return (
    <form onSubmit={handleSubmit} style={{ width: "100%", maxWidth: 760, margin: "0 auto" }}>
      <div style={{
        display: "flex", alignItems: "center", gap: 12,
        background: "white", borderRadius: 12, padding: "10px 12px 10px 18px",
        boxShadow: "0 2px 12px rgba(0,0,0,0.15)", border: "1.5px solid transparent",
      }}>
        <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="#718096" strokeWidth="2" style={{ flexShrink: 0 }}>
          <circle cx="11" cy="11" r="8" /><path strokeLinecap="round" d="M21 21l-4.35-4.35" />
        </svg>
        <input
          value={query}
          onChange={e => setQuery(e.target.value)}
          placeholder="e.g. Cheap flight from JFK to LA on Aug 15, no long layovers…"
          disabled={isLoading}
          style={{
            flex: 1, border: "none", outline: "none", fontSize: 15,
            color: "#1a1a2e", background: "transparent",
            fontFamily: "inherit",
          }}
        />
        <button
          type="submit"
          disabled={isLoading || !query.trim()}
          style={{
            flexShrink: 0, background: isLoading || !query.trim() ? "#93b4d4" : "var(--navy)",
            color: "white", border: "none", borderRadius: 8, padding: "10px 22px",
            fontSize: 14, fontWeight: 600, cursor: isLoading || !query.trim() ? "not-allowed" : "pointer",
            fontFamily: "inherit", transition: "background 0.2s",
          }}
        >
          {isLoading ? "Searching…" : "Search flights"}
        </button>
      </div>
      {!isLoading && (
        <div style={{ display: "flex", gap: 8, marginTop: 10, flexWrap: "wrap", justifyContent: "center" }}>
          {EXAMPLES.map(ex => (
            <button key={ex} type="button" onClick={() => setQuery(ex)} style={{
              background: "rgba(255,255,255,0.15)", color: "rgba(255,255,255,0.85)",
              border: "1px solid rgba(255,255,255,0.25)", borderRadius: 20,
              padding: "5px 14px", fontSize: 12, cursor: "pointer",
              fontFamily: "inherit", transition: "background 0.15s",
            }}
              onMouseEnter={e => e.target.style.background = "rgba(255,255,255,0.25)"}
              onMouseLeave={e => e.target.style.background = "rgba(255,255,255,0.15)"}
            >
              {ex}
            </button>
          ))}
        </div>
      )}
    </form>
  );
}