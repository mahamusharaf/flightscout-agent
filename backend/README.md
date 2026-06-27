# FlightScout

A flight search tool that doesn't just sort by price. FlightScout scores real flight offers across **price, layovers, and comfort**, then uses a LangChain agent to reason through the tradeoffs and explain *why* one flight beats another — not just *that* it does.

> "$40 more, but skips a layover and lands at 2pm instead of midnight" — that's the kind of answer a price-sort can't give you, and the kind of answer this project is built to produce.

**Status: in progress.** The deterministic data pipeline (API integration, normalization, scoring) is complete and tested against live data. The LangChain agent and React frontend are actively being built — see [Roadmap](#roadmap) below.

---

## Why this exists

Most "flight finder" tutorials wrap a single API call in a chatbot and call it agentic AI. FlightScout is built around a different idea: the *reasoning* (price vs. layovers vs. comfort) should be deterministic and testable, and the LLM's job should be limited to explaining a decision that's already been made — not making the decision itself.

This split matters for a concrete reason: ask an LLM to rank 56 flights by "best deal" and you'll get a plausible-sounding answer that may not be reproducible, isn't cheap to compute at scale, and can't be unit tested. A hand-built scoring function can be all three. The agent layer sits on top of that scoring function — it parses what the user actually wants, calls the scoring tool, and turns the numeric result into a natural-language explanation.

## How it works

```
Natural language query
   ("cheap flight to LA, don't want a long layover")
        │
        ▼
 Constraint parser (LLM)  →  structured search parameters
        │
        ▼
 Duffel API search  →  raw flight offers
        │
        ▼
 Normalizer  →  clean, typed FlightOffer objects
        │
        ▼
 Scoring engine (pure math, no LLM)  →  price / layover / comfort scores
        │
        ▼
 Explainer (LLM)  →  natural-language tradeoff explanation
        │
        ▼
 Ranked, explained results
```

## Tech stack

- **Backend:** FastAPI, Python
- **Agent framework:** LangChain (`AgentExecutor` + custom tools)
- **Flight data:** [Duffel API](https://duffel.com) 
- **Frontend:** React
- **LLM provider:** 
