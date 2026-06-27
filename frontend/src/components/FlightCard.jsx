import React from 'react';
import { Plane, Clock, ArrowRight, Info, Sparkles } from 'lucide-react';

export default function FlightCard({ offer, onOpenBreakdown }) {
  const slice = offer.slices[0];
  const firstSeg = slice?.segments[0];
  const lastSeg = slice?.segments[slice.segments.length - 1];

  const formatTime = (isoStr) => {
    if (!isoStr) return '';
    const dt = new Date(isoStr);
    return dt.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const formatDuration = (mins) => {
    const hrs = Math.floor(mins / 60);
    const m = mins % 60;
    return `${hrs}h ${m}m`;
  };

  const getTagClass = (badge) => {
    if (badge.includes('Top')) return 'tag-badge tag-top';
    if (badge.includes('Cheap') || badge.includes('Value')) return 'tag-badge tag-cheap';
    if (badge.includes('Fast')) return 'tag-badge tag-fast';
    return 'tag-badge tag-nonstop';
  };

  return (
    <div className="glass-card" style={{ padding: '1.5rem', marginBottom: '1.25rem', position: 'relative', overflow: 'hidden' }}>
      {/* Top Bar with Airline & Badges */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
          {offer.airline_logo ? (
            <img src={offer.airline_logo} alt={offer.airline_name} style={{ width: 36, height: 36, borderRadius: '8px', background: '#fff', padding: '2px' }} />
          ) : (
            <div style={{ width: 36, height: 36, borderRadius: '8px', background: 'var(--primary)', display: 'flex', alignItems: 'center', justifyCenter: 'center', color: '#fff', fontWeight: 700 }}>
              {offer.airline_name.substring(0, 2).toUpperCase()}
            </div>
          )}
          <div>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-main)' }}>{offer.airline_name}</h3>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{firstSeg?.flight_number || 'Direct'} • {offer.cabin_class.replace('_', ' ')}</span>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
          {offer.badges.map((badge, idx) => (
            <span key={idx} className={getTagClass(badge)}>{badge}</span>
          ))}
        </div>
      </div>

      {/* Main Itinerary Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr auto 1fr auto', alignItems: 'center', gap: '1.5rem', padding: '1rem 0', borderTop: '1px solid var(--border-glass)', borderBottom: '1px solid var(--border-glass)' }}>
        {/* Departure */}
        <div>
          <div style={{ fontSize: '1.5rem', fontWeight: 700, fontFamily: 'Outfit' }}>{formatTime(firstSeg?.departing_at)}</div>
          <div style={{ fontWeight: 600, color: 'var(--accent)' }}>{slice?.origin}</div>
        </div>

        {/* Flight Line & Duration */}
        <div style={{ textAlign: 'center', minWidth: '120px' }}>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.25rem', marginBottom: '0.2rem' }}>
            <Clock size={14} /> {formatDuration(offer.total_duration_minutes)}
          </div>
          <div style={{ position: 'relative', height: '2px', background: 'var(--border-accent)', margin: '0.4rem 0' }}>
            <Plane size={16} style={{ position: 'absolute', top: '-7px', left: '50%', transform: 'translateX(-50%) rotate(90deg)', color: 'var(--primary)' }} />
          </div>
          <div style={{ fontSize: '0.75rem', color: offer.total_layovers === 0 ? 'var(--success)' : 'var(--warning)', fontWeight: 600 }}>
            {offer.total_layovers === 0 ? 'Nonstop' : `${offer.total_layovers} Stop (${slice?.segments[0]?.destination})`}
          </div>
        </div>

        {/* Arrival */}
        <div style={{ textAlign: 'right' }}>
          <div style={{ fontSize: '1.5rem', fontWeight: 700, fontFamily: 'Outfit' }}>{formatTime(lastSeg?.arriving_at)}</div>
          <div style={{ fontWeight: 600, color: 'var(--accent)' }}>{slice?.destination}</div>
        </div>

        {/* Price & Score */}
        <div style={{ textAlign: 'right', paddingLeft: '1.5rem', borderLeft: '1px solid var(--border-glass)' }}>
          <div style={{ fontSize: '1.75rem', fontWeight: 800, fontFamily: 'Outfit', color: 'var(--text-main)' }}>
            ${offer.total_amount.toFixed(0)}
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginTop: '0.3rem', justifyContent: 'flex-end' }}>
            <div className="score-badge">{offer.overall_score.toFixed(0)}</div>
            <button 
              onClick={() => onOpenBreakdown(offer)}
              style={{ background: 'rgba(255,255,255,0.06)', border: '1px solid var(--border-glass)', borderRadius: '8px', padding: '0.4rem 0.6rem', color: 'var(--text-muted)', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.3rem', fontSize: '0.75rem' }}
            >
              <Info size={14} /> Math
            </button>
          </div>
        </div>
      </div>

      {/* Trade-off Explanation Banner */}
      {offer.tradeoff_explanation && (
        <div style={{ marginTop: '1rem', display: 'flex', alignItems: 'flex-start', gap: '0.5rem', fontSize: '0.85rem', color: 'var(--text-muted)', background: 'rgba(0,0,0,0.2)', padding: '0.75rem 1rem', borderRadius: 'var(--radius-sm)' }}>
          <Sparkles size={16} style={{ color: 'var(--accent)', flexShrink: 0, marginTop: '2px' }} />
          <span>{offer.tradeoff_explanation}</span>
        </div>
      )}
    </div>
  );
}
