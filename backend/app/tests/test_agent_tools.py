import pytest
from app.agent.constraint_parser import parse_natural_language_query
from app.agent.tools.search_tool import run_flight_search

def test_constraint_parser():
    res = parse_natural_language_query("Find cheap flight with nonstop preferred")
    prefs = res["preferences"]
    assert prefs.price_weight > prefs.speed_weight
    assert prefs.layover_tolerance == "direct_only"

def test_search_tool_mock():
    offers = run_flight_search("JFK", "LHR", "2026-08-01")
    assert len(offers) > 0
    assert offers[0].slices[0].origin == "JFK"
