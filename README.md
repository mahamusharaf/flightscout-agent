# FlightScout 

> **Agentic AI Flight Search, Multi-Criteria Scoring Engine & Trade-Off Explainer**

FlightScout is an intelligent flight decision-support platform. It empowers users to express flight preferences in natural language (e.g., *"Find me a fast, affordable flight to London with no layovers"*), extracts structured search constraints, queries live flight offers via the **Duffel API** (with high-fidelity mock fallback), computes deterministic weighted utility scores for each offer, and explains trade-offs in natural language.

---
# Why this exists

Most "flight finder" tutorials wrap a single API call in a chatbot and call it agentic AI. FlightScout is built around a different idea: the reasoning (price vs. layovers vs. comfort) should be deterministic and testable, and the LLM's job should be limited to explaining a decision that's already been made — not making the decision itself.

This split matters for a concrete reason: ask an LLM to rank 56 flights by "best deal" and you'll get a plausible-sounding answer that may not be reproducible, isn't cheap to compute at scale, and can't be unit tested. A hand-built scoring function can be all three. The agent layer sits on top of that scoring function — it parses what the user actually wants, calls the scoring tool, and turns the numeric result into a natural-language explanation.

# Tech stack

Backend: FastAPI, Python
Agent framework: LangChain (AgentExecutor + custom tools)
Flight data: Duffel API — chosen after Amadeus's self-service developer portal announced its shutdown mid-project 
Frontend: React
LLM provider: TBD (Groq Llama 3.3 70B)
