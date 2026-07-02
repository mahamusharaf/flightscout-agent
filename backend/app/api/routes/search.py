"""
Search API routes: two endpoints mirroring the project's own internal
boundary between constraint parsing and the deterministic search pipeline.

POST /search/parse  -- natural language -> structured SearchRequest only.
                        Lets the frontend show "here's what we understood"
                        and let the user confirm/edit before committing to
                        a real (slower, API-call-consuming) search.

POST /search         -- structured SearchRequest -> full ranked, explained
                         results. Called either after the user confirms a
                         parsed request, or directly from a form that
                         builds a SearchRequest without going through NL
                         parsing at all.

Both endpoints return clear, structured error responses (not raw Python
tracebacks) for the two known failure categories from the agent layer:
ConstraintParseError (ambiguous/incomplete query) and AgentSearchError
(search succeeded in parsing but failed downstream, e.g. no offers found).
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.agent.agent import AgentSearchError, run_flight_search, search_and_explain
from app.agent.constraint_parser import ConstraintParseError, parse_query
from app.models.schemas import ScoredFlightOffer, SearchRequest

router = APIRouter(prefix="/search", tags=["search"])


class ParseQueryRequest(BaseModel):
    query: str


class ParseQueryResponse(BaseModel):
    parsed_request: SearchRequest


class NaturalLanguageSearchResponse(BaseModel):
    summary: str
    parsed_request: SearchRequest
    results: list[ScoredFlightOffer]


class StructuredSearchResponse(BaseModel):
    results: list[ScoredFlightOffer]


@router.post("/parse", response_model=ParseQueryResponse)
def parse_search_query(body: ParseQueryRequest) -> ParseQueryResponse:
    """
    Parses a natural language query into a structured SearchRequest WITHOUT
    running the actual flight search. Intended for the frontend to show
    "here's what we understood" and let the user confirm or edit fields
    before triggering the slower, API-call-consuming /search endpoint.
    """
    try:
        parsed_request = parse_query(body.query)
    except ConstraintParseError as e:
        raise HTTPException(
            status_code=422,
            detail={
                "error": "constraint_parse_error",
                "message": str(e),
                "ambiguity_note": getattr(e.parsed, "ambiguity_note", None) if e.parsed else None,
            },
        ) from e

    return ParseQueryResponse(parsed_request=parsed_request)


@router.post("/natural-language", response_model=NaturalLanguageSearchResponse)
def search_from_natural_language(body: ParseQueryRequest) -> NaturalLanguageSearchResponse:
    """
    Full pipeline in one call: natural language query -> parse -> search ->
    score -> explain -> summary. Convenience endpoint for cases where the
    frontend wants to skip the confirm-before-searching step and just go.
    """
    try:
        result = run_flight_search(body.query)
    except ConstraintParseError as e:
        raise HTTPException(
            status_code=422,
            detail={
                "error": "constraint_parse_error",
                "message": str(e),
                "ambiguity_note": getattr(e.parsed, "ambiguity_note", None) if e.parsed else None,
            },
        ) from e
    except AgentSearchError as e:
        raise HTTPException(
            status_code=502,
            detail={"error": "agent_search_error", "message": str(e)},
        ) from e

    return NaturalLanguageSearchResponse(
        summary=result["summary"],
        parsed_request=result["parsed_request"],
        results=result["top_results"],
    )


@router.post("", response_model=StructuredSearchResponse)
def search_flights(request: SearchRequest) -> StructuredSearchResponse:
    """
    Runs the full search -> score -> explain pipeline against an already-
    structured SearchRequest (no natural language parsing involved). Used
    either after the frontend confirms a parsed request from /search/parse,
    or when a request is built directly from a structured form.

    Delegates to search_and_explain in agent.py -- the same function
    run_flight_search uses internally after parsing -- so this logic
    exists in exactly one place, not duplicated between the agent and API
    layers.
    """
    try:
        top_results = search_and_explain(request)
    except AgentSearchError as e:
        raise HTTPException(
            status_code=502,
            detail={"error": "agent_search_error", "message": str(e)},
        ) from e

    return StructuredSearchResponse(results=top_results)