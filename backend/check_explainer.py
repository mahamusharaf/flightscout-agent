import os
import sys
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if not os.environ.get("DUFFEL_TEST_TOKEN"):
    print("Set DUFFEL_TEST_TOKEN environment variable first.")
    sys.exit(1)
if not os.environ.get("GROQ_API_KEY"):
    print("Set GROQ_API_KEY environment variable first.")
    sys.exit(1)

from app.agent.tools.explainer_tool import explain_top_flights_tool
from app.agent.tools.scoring_tool import score_flights_tool
from app.agent.tools.search_tool import search_flights_tool

print("Searching flights (JFK -> LAX, 2026-08-15)...")
offers = search_flights_tool.invoke(
    {
        "origin_iata": "JFK",
        "destination_iata": "LAX",
        "departure_date": "2026-08-15",
    }
)
print(f"Got {len(offers)} offers")

print("Scoring...")
scored = score_flights_tool.invoke({"offers": offers})
print(f"Scored and sorted {len(scored)} offers")

print("Generating explanations for top 5...\n")
explained = explain_top_flights_tool.invoke({"scored_offers": scored, "top_n": 5})

print("=" * 70)
for i, result in enumerate(explained[:5], start=1):
    o = result.offer
    print(
        f"#{i}  {o.total_amount:.2f} {o.total_currency}  |  "
        f"{o.total_layover_count} stop(s)  |  {o.total_duration_minutes}min  |  "
        f"{o.cabin_class.value}  |  {o.departure_time_band.value}"
    )
    print(f"    \"{result.score.explanation}\"")
    print()

print("EXPLAINER E2E CHECK COMPLETE")
print()
print("Read the explanations above critically:")
print("  - Do they sound natural, or generic/templated?")
print("  - Do they actually reference the real numbers, or are they vague?")
print("  - Does #1's explanation make sense as standalone (no comparison)?")
print("  - Do #2-5 actually compare against the one above them meaningfully?")