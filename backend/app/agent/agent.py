from __future__ import annotations

from langchain.agents import create_agent

from app.agent.constraint_parser import ConstraintParseError, parse_query
from app.agent.tools.explainer_tool import explain_top_flights_tool
from app.config import DEFAULT_MODEL_NAME
from app.core.duffel_client import DuffelClient, DuffelClientError
from app.core.normalizer import normalize_offers
from app.core.scoring import score_offers
from app.models.schemas import ScoredFlightOffer, SearchRequest

_TOP_N_TO_EXPLAIN = 5

_SUMMARY_SYSTEM_PROMPT = """You write a short, friendly summary introducing a list of flight \
results to a traveler. The flights and their explanations are already finalized and correct --
your only job is to write 1-2 introductory sentences setting up the list (e.g. mentioning the
route and how many options were found). Do not list the flights yourself, do not restate their
prices or explanations, and do not invent any details. The actual flight list will be displayed
separately, right after your summary."""


class AgentSearchError(Exception):
    pass


def _build_summary_agent():
    return create_agent(
        model=f"groq:{DEFAULT_MODEL_NAME}",
        tools=[],
        system_prompt=_SUMMARY_SYSTEM_PROMPT,
    )


def search_and_explain(request: SearchRequest) -> list[ScoredFlightOffer]:
    client = DuffelClient()
    try:
        raw_offers = client.search_offers(
            origin_iata=request.origin_iata,
            destination_iata=request.destination_iata,
            departure_date=request.departure_date,
            return_date=request.return_date,
            cabin_class=request.cabin_class.value,
            adults=request.adults,
        )
    except DuffelClientError as e:
        raise AgentSearchError(
            f"Flight search failed (status {e.status_code}): {e.body}"
        ) from e

    offers = normalize_offers(raw_offers)
    if not offers:
        raise AgentSearchError(
            f"No flight offers found for {request.origin_iata} -> "
            f"{request.destination_iata} on {request.departure_date}."
        )

    scores = score_offers(offers, weights=request.weights)
    offer_by_id = {o.offer_id: o for o in offers}
    scored = [
        ScoredFlightOffer(offer=offer_by_id[s.offer_id], score=s) for s in scores
    ]
    scored.sort(key=lambda r: r.score.overall_score, reverse=True)

    # Direct Python call -- NOT through the agent. This is the fix for the
    # data-fabrication bug: explain_top_flights_tool is a normal callable,
    # we don't need an LLM to "decide" to call it or to transcribe its
    # arguments through free text.
    try:
        top_results = explain_top_flights_tool.invoke(
            {"scored_offers": scored, "top_n": _TOP_N_TO_EXPLAIN}
        )
    except Exception as e:
        raise AgentSearchError(f"Explanation step failed: {e}") from e

    return top_results[:_TOP_N_TO_EXPLAIN]


def run_flight_search(query: str) -> dict:
    parsed_request: SearchRequest = parse_query(query)

    top_results = search_and_explain(parsed_request)

    summary_agent = _build_summary_agent()
    summary_prompt = (
        f"Write a short intro for {len(top_results)} flight results from "
        f"{parsed_request.origin_iata} to {parsed_request.destination_iata} "
        f"on {parsed_request.departure_date}."
    )
    try:
        result = summary_agent.invoke(
            {"messages": [{"role": "user", "content": summary_prompt}]}
        )
    except Exception as e:
        raise AgentSearchError(f"Summary generation failed: {e}") from e

    messages = result.get("messages", [])
    summary = messages[-1].content if messages else ""

    return {
        "parsed_request": parsed_request,
        "summary": summary,
        "top_results": top_results,
        "raw_messages": messages,
    }