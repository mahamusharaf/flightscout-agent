const STEPS = [
    {
        n: "01",
        title: "Parse your request",
        desc: "A LangChain agent turns your sentence into a structured search — route, dates, cabin class, and what you actually care about.",
        icon: (
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--blue)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M4 6h16M4 12h10M4 18h7" />
            </svg>
        ),
    },
    {
        n: "02",
        title: "Search live fares",
        desc: "The structured query hits the Duffel API. Durations, prices, and offers are normalized and de-duplicated.",
        icon: (
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--blue)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="11" cy="11" r="7" /><path d="M21 21l-4.3-4.3" />
            </svg>
        ),
    },
    {
        n: "03",
        title: "Score every option",
        desc: "A weighted engine scores each flight on price, layovers, and comfort — tuned to what you said mattered.",
        icon: (
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--blue)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M4 19V10M12 19V4M20 19v-7" />
            </svg>
        ),
    },
    {
        n: "04",
        title: "Explain the tradeoff",
        desc: "The agent writes a plain-English reason for each ranking, so you know why a flight scored the way it did — not just that it did.",
        icon: (
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--blue)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z" />
            </svg>
        ),
    },
];

export default function HowItWorks() {
    return (
        <section style={{ maxWidth: 760, margin: "0 auto", padding: "8px 0 4px" }}>
            <div style={{ textAlign: "center", marginBottom: 28 }}>
                <span style={{
                    fontSize: 11, fontWeight: 700, color: "var(--blue)",
                    letterSpacing: "0.08em", textTransform: "uppercase",
                }}>
                    How it works
                </span>
                <h2 style={{
                    margin: "6px 0 0", fontSize: 20, fontWeight: 700,
                    color: "var(--navy)", letterSpacing: "-0.01em",
                }}>
                    One sentence in, a ranked, reasoned shortlist out
                </h2>
            </div>

            <div style={{ position: "relative" }}>
                {/* connecting line */}
                <div style={{
                    position: "absolute", top: 24, left: "12.5%", right: "12.5%",
                    height: 1, background: "var(--border)", zIndex: 0,
                }} />

                <div style={{
                    display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))", gap: 20,
                    position: "relative", zIndex: 1,
                }}>
                    {STEPS.map((step) => (
                        <div key={step.n} style={{ display: "flex", flexDirection: "column", alignItems: "center", textAlign: "center" }}>
                            <div style={{
                                width: 48, height: 48, borderRadius: 12,
                                background: "white", border: "1px solid var(--border)",
                                boxShadow: "var(--shadow)",
                                display: "flex", alignItems: "center", justifyContent: "center",
                                marginBottom: 10,
                            }}>
                                {step.icon}
                            </div>
                            <span style={{
                                fontSize: 10, fontWeight: 700, color: "var(--text-muted)",
                                letterSpacing: "0.06em", marginBottom: 4,
                            }}>
                                {step.n}
                            </span>
                            <h3 style={{ margin: "0 0 4px", fontSize: 13.5, fontWeight: 700, color: "var(--text)" }}>
                                {step.title}
                            </h3>
                            <p style={{ margin: 0, fontSize: 12, color: "var(--text-muted)", lineHeight: 1.5 }}>
                                {step.desc}
                            </p>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
}