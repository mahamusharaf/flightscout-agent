const API_BASE = "https://flightscout-agent.onrender.com";

export class ApiError extends Error {
  constructor(status, errorType, message, detail) {
    super(message);
    this.status = status;
    this.errorType = errorType;
    this.detail = detail;
  }
}

export async function searchFlightsNaturalLanguage(query) {
  const res = await fetch(`${API_BASE}/search/natural-language`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query }),
  });
  const body = await res.json().catch(() => null);
  if (!res.ok) {
    const d = body?.detail;
    throw new ApiError(res.status, d?.error ?? "unknown_error", d?.message ?? "Search failed.", d);
  }
  return body;
}
