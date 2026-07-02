const WEIGHTS = [
    { key: "price_weight", label: "Price" },
    { key: "layover_weight", label: "Layovers" },
    { key: "comfort_weight", label: "Comfort" },
];

export default function ParsedQueryBanner({ parsedRequest, summary }) {
    const w = parsedRequest.weights;
    const top = w ? WEIGHTS.reduce((a, b) => w[a.key] >= w[b.key] ? a : b).label.toLowerCase() : null;

    return (
        <div style={{ marginBottom: 20 }}>
            <div style={{
                background: "white", borderRadius: 10, padding: "12px 16px",
                boxShadow: "var(--shadow)", display: "flex", flexWrap: "wrap",
                alignItems: "center", gap: 6, fontSize: 13,
            }}>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--green)" strokeWidth="2.5">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span style={{ fontWeight: 600, color: "var(--navy)" }}>
                    {parsedRequest.origin_iata} → {parsedRequest.destination_iata}
                </span>
                <span style={{ color: "var(--text-muted)" }}>·</span>
                <span style={{ color: "var(--text-secondary)" }}>{parsedRequest.departure_date}</span>
                {parsedRequest.return_date && <>
                    <span style={{ color: "var(--text-muted)" }}>–</span>
                    <span style={{ color: "var(--text-secondary)" }}>{parsedRequest.return_date}</span>
                </>}
                <span style={{ color: "var(--text-muted)" }}>·</span>
                <span style={{ color: "var(--text-secondary)" }}>{parsedRequest.cabin_class.replace("_", " ")}</span>
                {top && <>
                    <span style={{ color: "var(--text-muted)" }}>·</span>
                    <span style={{ color: "var(--text-secondary)" }}>
                        optimizing for <strong style={{ color: "var(--navy)" }}>{top}</strong>
                    </span>
                </>}
            </div>
            {summary && (
                <p style={{ fontSize: 13, color: "var(--text-muted)", margin: "8px 4px 0", lineHeight: 1.5 }}>
                    {summary}
                </p>
            )}
        </div>
    );
}