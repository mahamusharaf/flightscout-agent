import { useEffect, useState } from "react";

const STAGES = [
    { label: "Understanding your search…", icon: "🧠" },
    { label: "Searching live flight offers…", icon: "✈️" },
    { label: "Scoring price, layovers and comfort…", icon: "⚖️" },
    { label: "Writing your tradeoff explanations…", icon: "✍️" },
];
const DURATIONS = [1400, 2000, 800, 3500];

export default function SearchLoadingState() {
    const [stage, setStage] = useState(0);

    useEffect(() => {
        if (stage >= STAGES.length - 1) return;
        const t = setTimeout(() => setStage(s => s + 1), DURATIONS[stage]);
        return () => clearTimeout(t);
    }, [stage]);

    return (
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", padding: "60px 20px", gap: 24 }}>
            <div style={{ position: "relative", width: 56, height: 56 }}>
                <div style={{
                    position: "absolute", inset: 0, borderRadius: "50%",
                    border: "3px solid #e2e8f0",
                }} />
                <div style={{
                    position: "absolute", inset: 0, borderRadius: "50%",
                    border: "3px solid var(--blue)", borderTopColor: "transparent",
                    animation: "spin 0.8s linear infinite",
                }} />
                <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
            </div>

            <div style={{ textAlign: "center" }}>
                <p style={{ fontSize: 16, fontWeight: 600, color: "var(--text)", margin: "0 0 6px" }}>
                    {STAGES[stage].icon} {STAGES[stage].label}
                </p>
                <p style={{ fontSize: 13, color: "var(--text-muted)", margin: 0 }}>
                    This usually takes 5–10 seconds
                </p>
            </div>

            <div style={{ display: "flex", gap: 6 }}>
                {STAGES.map((_, i) => (
                    <div key={i} style={{
                        height: 4, width: 32, borderRadius: 2,
                        background: i <= stage ? "var(--blue)" : "#e2e8f0",
                        transition: "background 0.4s",
                    }} />
                ))}
            </div>

            <div style={{
                background: "white", borderRadius: 12, padding: "16px 24px",
                boxShadow: "var(--shadow)", maxWidth: 400, width: "100%",
            }}>
                {STAGES.map((s, i) => (
                    <div key={i} style={{
                        display: "flex", alignItems: "center", gap: 10,
                        padding: "6px 0",
                        opacity: i <= stage ? 1 : 0.3,
                        transition: "opacity 0.4s",
                    }}>
                        <div style={{
                            width: 20, height: 20, borderRadius: "50%",
                            background: i < stage ? "var(--green)" : i === stage ? "var(--blue)" : "#e2e8f0",
                            display: "flex", alignItems: "center", justifyContent: "center",
                            flexShrink: 0, transition: "background 0.4s",
                        }}>
                            {i < stage && (
                                <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
                                    <path d="M2 5l2 2 4-4" stroke="white" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                                </svg>
                            )}
                        </div>
                        <span style={{ fontSize: 13, color: "var(--text-secondary)" }}>{s.label}</span>
                    </div>
                ))}
            </div>
        </div>
    );
}