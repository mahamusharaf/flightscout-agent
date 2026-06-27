import React, { useState } from 'react';
import { Search, Sparkles, Sliders, Calendar, MapPin, Users, Shield } from 'lucide-react';

export default function SearchForm({ onSearch, isLoading }) {
  const [formData, setFormData] = useState({
    origin: 'JFK',
    destination: 'LHR',
    departure_date: new Date(Date.now() + 14 * 86400000).toISOString().split('T')[0],
    passengers: 1,
    cabin_class: 'economy',
    natural_language_query: '',
    price_weight: 40,
    speed_weight: 30,
    comfort_weight: 30
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const totalW = Number(formData.price_weight) + Number(formData.speed_weight) + Number(formData.comfort_weight);
    const payload = {
      origin: formData.origin,
      destination: formData.destination,
      departure_date: formData.departure_date,
      passengers: Number(formData.passengers),
      cabin_class: formData.cabin_class,
      natural_language_query: formData.natural_language_query || null,
      preferences: {
        price_weight: Number(formData.price_weight) / totalW,
        speed_weight: Number(formData.speed_weight) / totalW,
        comfort_weight: Number(formData.comfort_weight) / totalW,
        layover_tolerance: 'any'
      }
    };
    onSearch(payload);
  };

  return (
    <div className="glass-card" style={{ padding: '2rem', marginBottom: '2.5rem' }}>
      <form onSubmit={handleSubmit}>
        {/* Natural Language Agent Query Box */}
        <div className="nl-box" style={{ marginBottom: '1.75rem' }}>
          <div style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--accent)', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.4rem', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
            <Sparkles size={16} /> AI Agent Natural Language Query (Optional)
          </div>
          <div style={{ position: 'relative' }}>
            <Sparkles className="nl-icon" size={20} />
            <input 
              type="text"
              name="natural_language_query"
              placeholder="e.g., 'Find me a budget flight under $600 with no layovers departing in the morning'"
              value={formData.natural_language_query}
              onChange={handleChange}
              className="nl-input"
            />
          </div>
        </div>

        {/* Structured Grid Form */}
        <div className="form-grid">
          <div className="form-group">
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}><MapPin size={14} /> Origin Airport</label>
            <input type="text" name="origin" value={formData.origin} onChange={handleChange} className="input-field" placeholder="e.g. JFK" required maxLength={3} />
          </div>

          <div className="form-group">
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}><MapPin size={14} /> Destination Airport</label>
            <input type="text" name="destination" value={formData.destination} onChange={handleChange} className="input-field" placeholder="e.g. LHR" required maxLength={3} />
          </div>

          <div className="form-group">
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}><Calendar size={14} /> Departure Date</label>
            <input type="date" name="departure_date" value={formData.departure_date} onChange={handleChange} className="input-field" required />
          </div>

          <div className="form-group">
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}><Users size={14} /> Passengers</label>
            <input type="number" name="passengers" min={1} max={9} value={formData.passengers} onChange={handleChange} className="input-field" required />
          </div>

          <div className="form-group">
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}><Shield size={14} /> Cabin Class</label>
            <select name="cabin_class" value={formData.cabin_class} onChange={handleChange} className="select-field">
              <option value="economy">Economy</option>
              <option value="premium_economy">Premium Economy</option>
              <option value="business">Business</option>
              <option value="first">First Class</option>
            </select>
          </div>
        </div>

        {/* Dynamic Preference Weight Sliders */}
        <div className="slider-group">
          <div className="slider-container">
            <div className="slider-header">
              <span>💰 Budget Weight</span>
              <strong>{formData.price_weight}%</strong>
            </div>
            <input type="range" name="price_weight" min={0} max={100} value={formData.price_weight} onChange={handleChange} />
          </div>

          <div className="slider-container">
            <div className="slider-header">
              <span>⚡ Speed Weight</span>
              <strong>{formData.speed_weight}%</strong>
            </div>
            <input type="range" name="speed_weight" min={0} max={100} value={formData.speed_weight} onChange={handleChange} />
          </div>

          <div className="slider-container">
            <div className="slider-header">
              <span>🛋️ Comfort Weight</span>
              <strong>{formData.comfort_weight}%</strong>
            </div>
            <input type="range" name="comfort_weight" min={0} max={100} value={formData.comfort_weight} onChange={handleChange} />
          </div>
        </div>

        <button type="submit" className="btn-primary" disabled={isLoading}>
          {isLoading ? (
            <>Running Agentic Agent Search...</>
          ) : (
            <>
              <Search size={20} /> Scout Best Flights
            </>
          )}
        </button>
      </form>
    </div>
  );
}
