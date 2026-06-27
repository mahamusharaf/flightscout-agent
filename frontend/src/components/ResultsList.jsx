import React, { useState } from 'react';
import FlightCard from './FlightCard';
import ScoreBreakdown from './ScoreBreakdown';
import { SlidersHorizontal, ArrowUpDown } from 'lucide-react';

export default function ResultsList({ searchResponse }) {
  const [selectedOffer, setSelectedOffer] = useState(null);
  const [sortBy, setSortBy] = useState('score'); // 'score', 'price', 'duration'

  if (!searchResponse) return null;

  const { query_summary, extracted_constraints, offers } = searchResponse;

  const sortedOffers = [...offers].sort((a, b) => {
    if (sortBy === 'price') return a.total_amount - b.total_amount;
    if (sortBy === 'duration') return a.total_duration_minutes - b.total_duration_minutes;
    return b.overall_score - a.overall_score; // default composite utility score
  });

  return (
    <div>
      {/* Search Header Summary */}
      <div className="glass-card" style={{ padding: '1.25rem 1.5rem', marginBottom: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h2 style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--text-main)' }}>Agent Search Results</h2>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>{query_summary}</p>
        </div>

        {/* Sort Controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <span style={{ fontSize: '0.85rem', color: 'var(--text-dim)', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
            <ArrowUpDown size={14} /> Sort By:
          </span>
          <select 
            value={sortBy} 
            onChange={(e) => setSortBy(e.target.value)}
            className="select-field"
            style={{ width: 'auto', padding: '0.4rem 0.8rem', fontSize: '0.85rem' }}
          >
            <option value="score">⚡ Agent Score (Utility)</option>
            <option value="price">💰 Price (Low to High)</option>
            <option value="duration">⏱️ Duration (Fastest)</option>
          </select>
        </div>
      </div>

      {/* Flight Cards Stream */}
      {sortedOffers.length === 0 ? (
        <div className="glass-card" style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
          No flights matched your strict filter parameters. Try expanding your search constraints.
        </div>
      ) : (
        sortedOffers.map((offer) => (
          <FlightCard 
            key={offer.id} 
            offer={offer} 
            onOpenBreakdown={(off) => setSelectedOffer(off)} 
          />
        ))
      )}

      {/* Score Math Modal */}
      {selectedOffer && (
        <ScoreBreakdown offer={selectedOffer} onClose={() => setSelectedOffer(null)} />
      )}
    </div>
  );
}
