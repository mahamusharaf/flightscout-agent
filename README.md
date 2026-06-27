# FlightScout ✈️

> **Agentic AI Flight Search, Multi-Criteria Scoring Engine & Trade-Off Explainer**

FlightScout is an intelligent flight decision-support platform. It empowers users to express flight preferences in natural language (e.g., *"Find me a fast, affordable flight to London with no layovers"*), extracts structured search constraints, queries live flight offers via the **Duffel API** (with high-fidelity mock fallback), computes deterministic weighted utility scores for each offer, and explains trade-offs in natural language.

---

## 🌟 Architecture & Features

- 🧠 **Autonomous Agent Pipeline**: Separates natural language parsing, carrier searching, multi-criteria scoring, and trade-off generation into clean, modular agent tools.
- 📐 **Deterministic Math Engine**: Evaluates flight offers on a composite 0-100 scale balancing Price, Duration, Layover Convenience, and Departure Time Match.
- 💬 **Trade-Off Explainer**: Highlights exact compromises (e.g. *"Saves $140 compared to direct, but adds a 1.5h layover"*).
- 🎨 **Glassmorphic Dark UI**: Built with React & Vite, featuring interactive math breakdown modals, real-time preference sliders, and badge highlights.
- 🔌 **Seamless API Fallback**: Runs out of the box with or without Duffel / LLM API keys.

---

## 📁 Repository Directory Structure

```
flightscout/
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI entrypoint, CORS & routes
│   │   ├── config.py                  # Settings & environment keys
│   │   ├── api/routes/                # Health check & search endpoints
│   │   ├── core/                      # Duffel API client, normalizer, scoring algorithm
│   │   ├── agent/                     # Autonomous agent executor, parser & tools
│   │   ├── models/                    # Pydantic V2 schemas & enums
│   │   └── tests/                     # Pytest suite for normalizer, scoring & agent tools
│   ├── requirements.txt
│   └── README.md
├── frontend/
│   ├── src/
│   │   ├── App.jsx                    # Main UI state & glassmorphic layout
│   │   ├── components/                # SearchForm, ResultsList, FlightCard, ScoreBreakdown
│   │   ├── api/                       # API fetch client
│   │   └── styles/                    # High-contrast HSL dark theme CSS
│   ├── package.json
│   └── vite.config.js
├── docs/
│   ├── architecture.md                # Sequence flow diagrams & design decisions
│   └── scoring-formula.md             # Complete mathematical utility formula
└── README.md
```

---

## 🚀 Quickstart Guide

### Prerequisites
- Python 3.10+
- Node.js 18+

### 1. Run the Backend (FastAPI)
```bash
cd backend
python -m venv venv
# On Windows: venv\Scripts\activate
# On Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 2. Run the Frontend (React + Vite)
In a new terminal:
```bash
cd frontend
npm install
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser!

---

## 🧪 Running Tests
To execute backend test suites:
```bash
cd backend
pytest
```
