import os
import sys
from datetime import date
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if not os.environ.get("GROQ_API_KEY"):
    print("Set GROQ_API_KEY environment variable first.")
    sys.exit(1)

from app.agent.constraint_parser import parse_query, ConstraintParseError

TEST_QUERIES = [
    "Flight from New York to Los Angeles on August 15th 2026",
    "I need a cheap flight from JFK to LAX next Friday, don't care about layovers",
    "Business class flight from London to Tokyo, comfort matters more than price, returning a week later",
    "Flight to Springfield",  # deliberately ambiguous — should flag low confidence
    "Flight from Lahore to Dubai in two weeks, budget under $400, prefer no long layovers",
]

print(f"Today's real date for reference: {date.today().isoformat()}\n")

for query in TEST_QUERIES:
    print(f"{'='*70}")
    print(f"QUERY: {query}")
    print(f"{'-'*70}")
    try:
        result = parse_query(query)
        print(f"  origin_iata:       {result.origin_iata}")
        print(f"  destination_iata:  {result.destination_iata}")
        print(f"  departure_date:    {result.departure_date}")
        print(f"  return_date:       {result.return_date}")
        print(f"  cabin_class:       {result.cabin_class.value}")
        print(f"  max_budget:        {result.max_budget}")
        print(f"  weights:           price={result.weights.price_weight}, "
              f"layover={result.weights.layover_weight}, "
              f"comfort={result.weights.comfort_weight}")
    except ConstraintParseError as e:
        print(f"  PARSE ERROR (expected for ambiguous queries): {e}")
    print()

print("CONSTRAINT PARSER E2E CHECK COMPLETE")