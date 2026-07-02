import { useState } from "react";
import SearchForm from "./components/SearchForm";
import SearchLoadingState from "./components/SearchLoadingState";
import ParsedQueryBanner from "./components/ParsedQueryBanner";
import FlightResultCard from "./components/FlightResultCard";
import SearchErrorState from "./components/SearchErrorState";
import HowItWorks from "./components/HowItWorks";
import { searchFlightsNaturalLanguage, ApiError } from "./api/flightApi";

const STATUS = { IDLE: "idle", LOADING: "loading", SUCCESS: "success", ERROR: "error" };

export default function App() {
  const [status, setStatus] = useState(STATUS.IDLE);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  async function handleSearch(query) {
    setStatus(STATUS.LOADING);
    setError(null);
    try {
      const data = await searchFlightsNaturalLanguage(query);
      setResult(data);
      setStatus(STATUS.SUCCESS);
    } catch (err) {
      setError(err instanceof ApiError ? err : new ApiError(0, "network_error", "Couldn't reach the server. Is the backend running?"));
      setStatus(STATUS.ERROR);
    }
  }

  function handleReset() {
    setStatus(STATUS.IDLE);
    setResult(null);
    setError(null);
  }

  const showForm = status !== STATUS.LOADING;

  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>
      {/* Navy header -- matches Vastwing's deep blue hero */}
      <header style={{
        background: "var(--navy)",
        backgroundImage: "linear-gradient(135deg, #0B2A4A 0%, #1a3d5c 100%)",
        padding: status === STATUS.SUCCESS ? "24px 20px 32px" : "56px 20px 64px",
        transition: "padding 0.4s ease",
      }}>
        {/* Logo */}
        <div style={{ maxWidth: 760, margin: "0 auto 0" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: status === STATUS.SUCCESS ? 16 : 28 }}>
            <div style={{
              width: 32, height: 32, background: "var(--blue)", borderRadius: 8,
              display: "flex", alignItems: "center", justifyContent: "center",
            }}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="white">
                <path d="M21 16v-2l-8-5V3.5c0-.83-.67-1.5-1.5-1.5S10 2.67 10 3.5V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5l8 2.5z" />
              </svg>
            </div>
            <span style={{ color: "white", fontWeight: 700, fontSize: 18, letterSpacing: "-0.01em" }}>
              FlightScout
            </span>
          </div>

          {status !== STATUS.SUCCESS && (
            <div style={{ textAlign: "center", marginBottom: 28 }}>
              <h1 style={{
                color: "white", fontSize: 30, fontWeight: 700, margin: "0 0 8px",
                letterSpacing: "-0.02em",
              }}>
                Find your best flight tradeoff
              </h1>
              <p style={{ color: "rgba(255,255,255,0.65)", fontSize: 15, margin: 0 }}>
                Tell us what matters — price, layovers, comfort — in plain English.
              </p>
            </div>
          )}

          {showForm && (
            <SearchForm onSearch={handleSearch} isLoading={status === STATUS.LOADING} />
          )}
        </div>
      </header>

      {/* Main content area */}
      <main style={{ flex: 1, padding: "28px 20px 48px" }}>
        <div style={{ maxWidth: 760, margin: "0 auto" }}>
          {status === STATUS.IDLE && <HowItWorks />}
          {status === STATUS.LOADING && <SearchLoadingState />}
          {status === STATUS.ERROR && error && <SearchErrorState error={error} onRetry={handleReset} />}
          {status === STATUS.SUCCESS && result && (
            <>
              <ParsedQueryBanner parsedRequest={result.parsed_request} summary={result.summary} />
              <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                {result.results.map((r, i) => (
                  <FlightResultCard key={r.offer.offer_id} result={r} rank={i + 1} />
                ))}
              </div>
              <div style={{ textAlign: "center", marginTop: 28 }}>
                <button onClick={handleReset} style={{
                  background: "transparent", color: "var(--navy)",
                  border: "1.5px solid var(--navy)", borderRadius: 8,
                  padding: "10px 22px", fontSize: 14, fontWeight: 600,
                  cursor: "pointer", fontFamily: "inherit",
                }}>
                  New search
                </button>
              </div>
            </>
          )}
        </div>
      </main>
    </div>
  );
}