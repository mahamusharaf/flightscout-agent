export default function SearchErrorState({ error, onRetry }) {
    const isAmbiguous = error.errorType === "constraint_parse_error";
    return (
        <div style={{ textAlign: "center", padding: "60px 20px" }}>
            <div style={{
                width: 52, height: 52, borderRadius: "50%", background: "#FEF3C7",
                display: "flex", alignItems: "center", justifyContent: "center",
                margin: "0 auto 16px",
            }}>
                <svg width="24" height="24" fill="none" viewBox="0 0 24 24" stroke="#D97706" strokeWidth="2">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
                </svg>
            </div>
            <h3 style={{ fontSize: 17, fontWeight: 600, color: "var(--text)", margin: "0 0 8px" }}>
                {isAmbiguous ? "Need a bit more detail" : "No flights found"}
            </h3>
            <p style={{ fontSize: 14, color: "var(--text-secondary)", margin: "0 0 6px", maxWidth: 360, marginLeft: "auto", marginRight: "auto" }}>
                {isAmbiguous
                    ? "Try including a clear origin, destination, and departure date."
                    : error.message}
            </p>
            {isAmbiguous && error.detail?.ambiguity_note && (
                <p style={{ fontSize: 12, color: "var(--text-muted)", fontStyle: "italic", margin: "0 0 16px" }}>
                    {error.detail.ambiguity_note}
                </p>
            )}
            <button onClick={onRetry} style={{
                marginTop: 16, background: "var(--navy)", color: "white",
                border: "none", borderRadius: 8, padding: "10px 22px",
                fontSize: 14, fontWeight: 600, cursor: "pointer", fontFamily: "inherit",
            }}>
                Try again
            </button>
        </div>
    );
}