from typing import Dict, Any
from app.models.schemas import SearchRequest, SearchResponse
from app.agent.constraint_parser import parse_natural_language_query
from app.agent.tools.search_tool import run_flight_search
from app.agent.tools.scoring_tool import run_flight_scoring
from app.agent.tools.explainer_tool import generate_tradeoff_explanations

class FlightScoutAgent:
    """
    Autonomous agent executor coordinating constraint extraction, offer searching, multi-criteria scoring, and trade-off generation.
    """
    def execute_search(self, request: SearchRequest) -> SearchResponse:
        # Step 1: Constraint & Preference parsing
        parsed = parse_natural_language_query(request.natural_language_query)
        effective_prefs = request.preferences or parsed["preferences"]
        
        # If NL query yielded specific preferences and request had defaults, merge them
        if request.natural_language_query and parsed["extracted_keywords"]:
            effective_prefs = parsed["preferences"]

        # Step 2: Tool 1 Execution (Flight Search)
        raw_offers = run_flight_search(
            origin=request.origin.upper(),
            destination=request.destination.upper(),
            departure_date=request.departure_date,
            passengers=request.passengers,
            cabin_class=request.cabin_class.value
        )

        # Apply hard constraint filters (e.g., layover tolerance, max price)
        filtered_offers = []
        for offer in raw_offers:
            if effective_prefs.max_price and offer.total_amount > effective_prefs.max_price:
                continue
            if effective_prefs.layover_tolerance == "direct_only" and offer.total_layovers > 0:
                continue
            if effective_prefs.layover_tolerance == "max_one" and offer.total_layovers > 1:
                continue
            filtered_offers.append(offer)

        # If strict filtering removed all options, keep original to avoid empty results
        final_offers_pool = filtered_offers if filtered_offers else raw_offers

        # Step 3: Tool 2 Execution (Scoring & Ranking)
        scored_offers = run_flight_scoring(final_offers_pool, effective_prefs)

        # Step 4: Tool 3 Execution (Trade-off Explanations)
        explained_offers = generate_tradeoff_explanations(scored_offers, effective_prefs)

        # Formulate query summary
        kw_str = ", ".join(parsed["extracted_keywords"]) if parsed["extracted_keywords"] else "Standard Criteria"
        summary = f"Found {len(explained_offers)} offers from {request.origin} to {request.destination} on {request.departure_date} ({kw_str})."

        return SearchResponse(
            query_summary=summary,
            extracted_constraints={
                "keywords": parsed["extracted_keywords"],
                "price_weight": effective_prefs.price_weight,
                "speed_weight": effective_prefs.speed_weight,
                "comfort_weight": effective_prefs.comfort_weight,
                "layover_tolerance": effective_prefs.layover_tolerance
            },
            total_offers_found=len(explained_offers),
            offers=explained_offers
        )

agent_executor = FlightScoutAgent()
