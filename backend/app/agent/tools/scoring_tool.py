from __future__ import annotations

from langchain.tools import tool

from app.core.scoring import score_offers
from app.models.schemas import FlightOffer, ScoredFlightOffer, ScoringWeights


@tool
def score_flights_tool(
    offers: list[FlightOffer], weights: ScoringWeights | None = None
) -> list[ScoredFlightOffer]:
    scores = score_offers(offers, weights=weights)

    offer_by_id = {o.offer_id: o for o in offers}
    results = [
        ScoredFlightOffer(offer=offer_by_id[s.offer_id], score=s) for s in scores
    ]
    results.sort(key=lambda r: r.score.overall_score, reverse=True)
    return results