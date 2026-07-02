import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if not os.environ.get("DUFFEL_TEST_TOKEN"):
    print("Set DUFFEL_TEST_TOKEN environment variable first.")
    sys.exit(1)
if not os.environ.get("GROQ_API_KEY"):
    print("Set GROQ_API_KEY environment variable first.")
    sys.exit(1)

from app.agent.agent import AgentSearchError, run_flight_search
from app.agent.constraint_parser import ConstraintParseError

QUERY = "I need a cheap flight from JFK to LAX on August 15th 2026, don't care much about layovers"

print(f"QUERY: {QUERY}\n")
print("Running full pipeline (parse -> search -> score -> explain -> summarize)...\n")

try:
    result = run_flight_search(QUERY)
except ConstraintParseError as e:
    print(f"CONSTRAINT PARSE ERROR: {e}")
    sys.exit(1)
except AgentSearchError as e:
    print(f"AGENT SEARCH ERROR: {e}")
    sys.exit(1)

print("=" * 70)
print("PARSED REQUEST:")
print(f"  {result['parsed_request']}")
print()
print("=" * 70)
print("LLM-WRITTEN SUMMARY:")
print(f"  {result['summary']}")
print()
print("=" * 70)
print(f"TOP {len(result['top_results'])} EXPLAINED RESULTS:")
for i, r in enumerate(result["top_results"], start=1):
    o = r.offer
    print(
        f"\n#{i}  {o.total_amount:.2f} {o.total_currency}  |  "
        f"{o.total_layover_count} stop(s)  |  {o.total_duration_minutes}min  |  "
        f"{o.cabin_class.value}  |  {o.departure_time_band.value}"
    )
    print(f'    "{r.score.explanation}"')

print()
print("=" * 70)
print("VERIFICATION: do these offer IDs/prices match what you've seen in earlier")
print("test runs for this same route/date? If they look fabricated or generic")
print("(round numbers, made-up airlines, wrong year), something is still wrong.")
print()
print("AGENT E2E CHECK COMPLETE")