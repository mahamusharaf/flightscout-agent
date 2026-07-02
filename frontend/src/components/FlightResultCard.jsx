function fmt(mins) {
  return `${Math.floor(mins / 60)}h ${mins % 60}m`;
}
function fmtTime(iso) {
  return new Date(iso).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", hour12: false });
}
function fmtPrice(amount, currency) {
  return `${Math.round(amount)} ${currency}`;
}

const BAND = {
  red_eye: "Red-eye", early_morning: "Early morning",
  daytime: "Daytime", evening: "Evening", late_night: "Late night",
};

export default function FlightResultCard({ result, rank }) {
  const { offer, score } = result;
  const slice = offer.slices[0];
  const first = slice.segments[0];
  const last = slice.segments[slice.segments.length - 1];
  const isTop = rank === 1;

  return (
    <div style={{
      background: "white", borderRadius: 14,
      border: isTop ? "2px solid var(--blue)" : "1px solid var(--border)",
      boxShadow: isTop ? "0 4px 16px rgba(26,115,232,0.12)" : "var(--shadow)",
      overflow: "hidden",
    }}>
      {isTop && (
        <div style={{
          background: "var(--blue)", color: "white",
          fontSize: 11, fontWeight: 700, letterSpacing: "0.06em",
          padding: "5px 14px", textTransform: "uppercase",
        }}>
          ★ Top pick
        </div>
      )}

      <div style={{ padding: "18px 20px" }}>
        {/* Header row: meta tags + price */}
        <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", marginBottom: 14 }}>
          <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
            <Tag color={offer.total_layover_count === 0 ? "green" : "grey"}>
              {offer.total_layover_count === 0 ? "Non-stop" : `${offer.total_layover_count} stop${offer.total_layover_count > 1 ? "s" : ""}`}
            </Tag>
            <Tag color="grey">{offer.cabin_class.replace("_", " ")}</Tag>
            <Tag color="grey">{BAND[offer.departure_time_band]}</Tag>
          </div>
          <div style={{ textAlign: "right", flexShrink: 0 }}>
            <div style={{ fontSize: 22, fontWeight: 700, color: "var(--navy)" }}>
              {fmtPrice(offer.total_amount, offer.total_currency)}
            </div>
            <div style={{ fontSize: 11, color: "var(--text-muted)" }}>per person</div>
          </div>
        </div>

        {/* Route row */}
        <div style={{ display: "flex", alignItems: "center", gap: 0, marginBottom: 14 }}>
          <div style={{ textAlign: "center", minWidth: 60 }}>
            <div style={{ fontSize: 22, fontWeight: 700, color: "var(--text)" }}>{fmtTime(first.departure_at)}</div>
            <div style={{ fontSize: 13, fontWeight: 600, color: "var(--text-secondary)" }}>{first.origin_iata}</div>
          </div>

          <div style={{ flex: 1, padding: "0 12px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
              <div style={{ flex: 1, height: 1, background: "var(--border)" }} />
              <svg width="16" height="16" viewBox="0 0 24 24" fill="var(--blue)" style={{ flexShrink: 0 }}>
                <path d="M21 16v-2l-8-5V3.5c0-.83-.67-1.5-1.5-1.5S10 2.67 10 3.5V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5l8 2.5z" />
              </svg>
              <div style={{ flex: 1, height: 1, background: "var(--border)" }} />
            </div>
            <div style={{ textAlign: "center", fontSize: 11, color: "var(--text-muted)", marginTop: 4 }}>
              {fmt(offer.total_duration_minutes)}
              {offer.total_layover_count > 0 && ` · ${fmt(offer.total_layover_duration_minutes)} layover`}
            </div>
          </div>

          <div style={{ textAlign: "center", minWidth: 60 }}>
            <div style={{ fontSize: 22, fontWeight: 700, color: "var(--text)" }}>{fmtTime(last.arrival_at)}</div>
            <div style={{ fontSize: 13, fontWeight: 600, color: "var(--text-secondary)" }}>{last.destination_iata}</div>
          </div>
        </div>

        {/* Score bar */}
        <div style={{
          display: "flex", gap: 8, marginBottom: score.explanation ? 14 : 0,
        }}>
          {[
            { label: "Price", val: score.price_score },
            { label: "Layover", val: score.layover_score },
            { label: "Comfort", val: score.comfort_score },
          ].map(({ label, val }) => (
            <div key={label} style={{ flex: 1 }}>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 3 }}>
                <span style={{ fontSize: 10, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.04em" }}>{label}</span>
                <span style={{ fontSize: 10, fontWeight: 600, color: "var(--text-secondary)" }}>{Math.round(val * 100)}</span>
              </div>
              <div style={{ height: 3, borderRadius: 2, background: "#e2e8f0", overflow: "hidden" }}>
                <div style={{
                  height: "100%", borderRadius: 2,
                  width: `${val * 100}%`,
                  background: val >= 0.7 ? "var(--green)" : val >= 0.4 ? "var(--blue)" : "#f59e0b",
                  transition: "width 0.6s ease",
                }} />
              </div>
            </div>
          ))}
        </div>

        {/* Explanation */}
        {score.explanation && (
          <div style={{
            background: "var(--blue-light)", borderRadius: 8,
            padding: "10px 12px", display: "flex", gap: 8, alignItems: "flex-start",
          }}>
            <span style={{ fontSize: 14, flexShrink: 0 }}>✦</span>
            <p style={{ margin: 0, fontSize: 13, color: "#1e3a5f", lineHeight: 1.55 }}>
              {score.explanation}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

function Tag({ children, color }) {
  const styles = {
    green: { background: "var(--green-light)", color: "var(--green)" },
    grey: { background: "#f1f5f9", color: "var(--text-secondary)" },
  };
  return (
    <span style={{
      fontSize: 11, fontWeight: 600, padding: "3px 9px", borderRadius: 12,
      ...styles[color],
    }}>{children}</span>
  );
}