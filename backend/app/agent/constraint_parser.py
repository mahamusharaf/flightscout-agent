from __future__ import annotations

from datetime import date
from typing import Optional

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from app.agent.date_resolver import RelativeDateExpression, resolve_relative_date
from app.config import get_llm
from app.models.enums import CabinClass
from app.models.schemas import ScoringWeights, SearchRequest


class ParsedConstraints(BaseModel):

    origin_iata: Optional[str] = Field(
        None, description="3-letter IATA code for the origin airport"
    )
    destination_iata: Optional[str] = Field(
        None, description="3-letter IATA code for the destination airport"
    )

    departure_date_absolute: Optional[str] = Field(
        None, description="YYYY-MM-DD if the user gave an explicit/absolute date, else null"
    )
    departure_date_relative: Optional[RelativeDateExpression] = Field(
        None, description="Structured relative date expression if the user used relative phrasing, else null"
    )

    return_date_absolute: Optional[str] = Field(None, description="YYYY-MM-DD or null")
    return_date_relative: Optional[RelativeDateExpression] = Field(None)

    cabin_class: str = Field("economy", description="economy, premium_economy, business, or first")
    adults: int = 1
    max_budget: Optional[float] = None

    # Inferred preference signals — these map to ScoringWeights, not raw
    # SearchRequest fields, because "I don't care about layovers" is a
    # weighting preference, not a hard filter.
    price_priority: str = Field(
        "medium", description="low, medium, or high — how much price should dominate the ranking"
    )
    layover_tolerance: str = Field(
        "medium", description="low, medium, or high — low means strongly prefer fewer/no layovers"
    )
    comfort_priority: str = Field(
        "medium", description="low, medium, or high"
    )

    confidence: str = Field(
        "high", description="high, medium, or low — your confidence in the IATA codes and dates extracted"
    )
    ambiguity_note: Optional[str] = Field(
        None, description="If confidence isn't high, briefly explain what's ambiguous (e.g. unclear city name, unresolvable relative date, or no date mentioned at all)"
    )


class ConstraintParseError(Exception):
    def __init__(self, message: str, parsed: Optional[ParsedConstraints] = None):
        self.parsed = parsed
        super().__init__(message)


_SYSTEM_PROMPT = """You extract structured flight search parameters from a user's natural language request.

Today's real date is {today}. You will use this ONLY for context about what counts as "soon" \
or "far away" — you must NOT do any date-of-week or calendar arithmetic yourself. Date \
arithmetic done by language models is unreliable and has caused real bugs (e.g. resolving \
"next Friday" to a Saturday). Instead, follow these rules strictly:

- If the user gives an ABSOLUTE date ("August 15th 2026", "on 2026-08-15"), put it in \
departure_date_absolute as YYYY-MM-DD, and leave departure_date_relative null.
- If the user gives a RELATIVE date ("next Friday", "in two weeks", "this weekend"), leave \
departure_date_absolute null, and instead fill departure_date_relative with its STRUCTURE only:
  - For a named weekday ("next Friday", "this Monday"): set weekday_name to the lowercase \
weekday, and weeks_ahead to 1 for "next <weekday>" phrasing (skip to the following week if \
today already is that weekday) or 0 for "this <weekday>" / soonest occurrence phrasing.
  - For a day/week count ("in two weeks", "in 5 days"): set days_offset to the total number \
of days (two weeks = 14 days).
- If the user does NOT mention a departure date at all, both departure_date_absolute and \
departure_date_relative MUST be null. Do NOT default to today's date or guess — a missing \
date should come back as null, full stop, even if everything else in the query is clear. \
Note this in ambiguity_note and lower confidence to "medium" if a date is genuinely required \
but absent.
- Apply the same absolute/relative split to return_date_absolute and return_date_relative.

For origin/destination, convert city or airport names to their 3-letter IATA airport code. \
If a city has multiple airports and the user didn't specify which one, pick the primary \
international airport, but set confidence to "medium" and explain the ambiguity in \
ambiguity_note. If you cannot confidently resolve a location at all, set confidence to "low".

For preference signals (price_priority, layover_tolerance, comfort_priority), infer from \
phrasing like "cheap", "don't care about price", "no long layovers", "I want to be comfortable" \
— if the user doesn't mention a dimension at all, leave it as "medium".

Respond with ONLY a JSON object matching this structure, no other text:
{{
  "origin_iata": "XXX or null",
  "destination_iata": "XXX or null",
  "departure_date_absolute": "YYYY-MM-DD or null",
  "departure_date_relative": {{"weekday_name": "string or null", "weeks_ahead": 1, "days_offset": "number or null"}} or null,
  "return_date_absolute": "YYYY-MM-DD or null",
  "return_date_relative": same structure as departure_date_relative, or null,
  "cabin_class": "economy|premium_economy|business|first",
  "adults": 1,
  "max_budget": number or null,
  "price_priority": "low|medium|high",
  "layover_tolerance": "low|medium|high",
  "comfort_priority": "low|medium|high",
  "confidence": "high|medium|low",
  "ambiguity_note": "string or null"
}}"""


def _build_chain():
    llm = get_llm(temperature=0.0)
    prompt = ChatPromptTemplate.from_messages(
        [("system", _SYSTEM_PROMPT), ("human", "{query}")]
    )
    parser = JsonOutputParser(pydantic_object=ParsedConstraints)
    return prompt | llm | parser


# Maps a low/medium/high preference signal to a concrete ScoringWeights
# adjustment. These are starting points, not precisely tuned — refine once
# real agent runs show whether "high layover_tolerance" actually produces
# rankings that feel right.
_PRICE_PRIORITY_TO_WEIGHT = {"low": 0.3, "medium": 0.5, "high": 0.7}
_LAYOVER_TOLERANCE_TO_WEIGHT = {"low": 0.45, "medium": 0.3, "high": 0.15}
_COMFORT_PRIORITY_TO_WEIGHT = {"low": 0.1, "medium": 0.2, "high": 0.35}


def _weights_from_signals(parsed: ParsedConstraints) -> ScoringWeights:
    price_w = _PRICE_PRIORITY_TO_WEIGHT[parsed.price_priority]
    layover_w = _LAYOVER_TOLERANCE_TO_WEIGHT[parsed.layover_tolerance]
    comfort_w = _COMFORT_PRIORITY_TO_WEIGHT[parsed.comfort_priority]

    total = price_w + layover_w + comfort_w
    price_weight = round(price_w / total, 4)
    layover_weight = round(layover_w / total, 4)
    # Derived, not rounded independently — guarantees exact sum of 1.0.
    comfort_weight = round(1.0 - price_weight - layover_weight, 4)

    return ScoringWeights(
        price_weight=price_weight,
        layover_weight=layover_weight,
        comfort_weight=comfort_weight,
    )


def _resolve_date_field(
    absolute: Optional[str],
    relative: Optional[RelativeDateExpression],
    today: date,
) -> Optional[str]:
    if absolute:
        return absolute
    if relative:
        return resolve_relative_date(relative, today).isoformat()
    return None


def parse_query(query: str, today: Optional[date] = None) -> SearchRequest:
    today = today or date.today()
    chain = _build_chain()

    raw_result = chain.invoke({"query": query, "today": today.isoformat()})
    parsed = ParsedConstraints.model_validate(raw_result)

    departure_date = _resolve_date_field(
        parsed.departure_date_absolute, parsed.departure_date_relative, today
    )
    return_date = _resolve_date_field(
        parsed.return_date_absolute, parsed.return_date_relative, today
    )

    missing = [
        field
        for field, value in [
            ("origin_iata", parsed.origin_iata),
            ("destination_iata", parsed.destination_iata),
            ("departure_date", departure_date),
        ]
        if not value
    ]
    if missing:
        raise ConstraintParseError(
            f"Could not extract required field(s): {', '.join(missing)}. "
            f"Ask the user to specify these explicitly.",
            parsed=parsed,
        )

    if parsed.confidence == "low":
        raise ConstraintParseError(
            f"Low confidence in extraction: {parsed.ambiguity_note or 'no detail given'}. "
            f"Ask the user to clarify.",
            parsed=parsed,
        )

    weights = _weights_from_signals(parsed)

    return SearchRequest(
        origin_iata=parsed.origin_iata,
        destination_iata=parsed.destination_iata,
        departure_date=departure_date,
        return_date=return_date,
        cabin_class=CabinClass(parsed.cabin_class),
        adults=parsed.adults,
        max_budget=parsed.max_budget,
        weights=weights,
    )