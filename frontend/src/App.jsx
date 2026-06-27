import React, { useState } from 'react';
import SearchForm from './components/SearchForm';
import ResultsList from './components/ResultsList';
import { searchFlights } from './api/flightApi';
import { Compass, Sparkles, AlertCircle } from 'lucide-react';

export default function App() {
  const [searchResponse, setSearchResponse] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async (searchPayload) => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await searchFlights(searchPayload);
      setSearchResponse(data);
    } catch (err) {
      setError(err.message || 'An unexpected error occurred while scouting flights.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-container">
      {/* Top Brand Header */}
      <header className="header">
        <div>
          <div className="brand">
            <div className="brand-icon">
              <Compass size={24} />
            </div>
            FlightScout
          </div>
          <p className="subtitle">AI-Agent Driven Flight Utility Scoring & Trade-off Explanations</p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', background: 'rgba(99, 102, 241, 0.1)', padding: '0.5rem 1rem', borderRadius: '20px', border: '1px solid var(--border-accent)', fontSize: '0.85rem', color: 'var(--accent)' }}>
          <Sparkles size={16} /> Powered by Duffel & Autonomous Agent Tooling
        </div>
      </header>

      {/* Main Form & Results Layout */}
      <main>
        <SearchForm onSearch={handleSearch} isLoading={isLoading} />

        {error && (
          <div className="glass-card" style={{ padding: '1.25rem', marginBottom: '2rem', borderColor: '#f43f5e', background: 'rgba(244, 63, 94, 0.1)', color: '#fda4af', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <AlertCircle size={20} style={{ flexShrink: 0 }} />
            <span>{error}</span>
          </div>
        )}

        <ResultsList searchResponse={searchResponse} />
      </main>
    </div>
  );
}
