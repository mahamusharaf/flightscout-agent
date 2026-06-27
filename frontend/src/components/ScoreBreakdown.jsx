import React from 'react';
import { X, Award, DollarSign, Clock, MapPin, Calendar } from 'lucide-react';

export default function ScoreBreakdown({ offer, onClose }) {
  if (!offer || !offer.score_breakdown) return null;

  const { price_score, duration_score, layover_score, schedule_score } = offer.score_breakdown;

  const metrics = [
    { label: 'Price Value', score: price_score, icon: DollarSign, color: '#10b981', desc: 'Competitiveness compared to overall route pricing pool.' },
    { label: 'Speed & Duration', score: duration_score, icon: Clock, color: '#38bdf8', desc: 'Total travel duration optimization.' },
    { label: 'Layover Convenience', score: layover_score, icon: MapPin, color: '#f59e0b', desc: 'Direct flights score 100, minimal stopovers score high.' },
    { label: 'Schedule Fit', score: schedule_score, icon: Calendar, color: '#8b5cf6', desc: 'Alignment with requested departure time of day.' },
  ];

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <Award style={{ color: 'var(--primary)' }} size={28} />
            <div>
              <h2 style={{ fontSize: '1.4rem', fontWeight: 700 }}>Score Math & Utility Breakdown</h2>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>{offer.airline_name} • Flight ID: {offer.id}</p>
            </div>
          </div>
          <button 
            onClick={onClose}
            style={{ background: 'transparent', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', padding: '0.25rem' }}
          >
            <X size={24} />
          </button>
        </div>

        <div style={{ textAlign: 'center', padding: '1.5rem', background: 'rgba(0,0,0,0.2)', borderRadius: 'var(--radius-md)', marginBottom: '1.5rem' }}>
          <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '1px', marginBottom: '0.25rem' }}>Overall Composite Utility</div>
          <div style={{ fontSize: '3.5rem', fontWeight: 800, fontFamily: 'Outfit', color: 'var(--text-main)' }}>
            {offer.overall_score} <span style={{ fontSize: '1.5rem', color: 'var(--text-muted)' }}>/ 100</span>
          </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          {metrics.map((m, i) => {
            const Icon = m.icon;
            return (
              <div key={i} style={{ background: 'var(--bg-glass)', padding: '1rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-glass)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 600 }}>
                    <Icon size={18} style={{ color: m.color }} />
                    {m.label}
                  </div>
                  <div style={{ fontWeight: 700, color: m.color }}>{m.score.toFixed(1)} / 100</div>
                </div>
                <div style={{ width: '100%', height: '8px', background: 'rgba(255,255,255,0.06)', borderRadius: '4px', overflow: 'hidden', marginBottom: '0.4rem' }}>
                  <div style={{ width: `${Math.min(100, Math.max(0, m.score))}%`, height: '100%', background: m.color, transition: 'width 0.6s ease' }} />
                </div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{m.desc}</div>
              </div>
            );
          })}
        </div>

        {offer.tradeoff_explanation && (
          <div style={{ marginTop: '1.5rem', padding: '1rem', background: 'rgba(99,102,241,0.1)', border: '1px solid var(--border-accent)', borderRadius: 'var(--radius-md)', fontSize: '0.9rem', lineHeight: '1.5' }}>
            <strong style={{ color: 'var(--accent)' }}>🤖 Agent Insight: </strong>
            {offer.tradeoff_explanation}
          </div>
        )}
      </div>
    </div>
  );
}
