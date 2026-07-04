from __future__ import annotations

from langchain.tools import tool
from langchain_core.prompts import ChatPromptTemplate

from app.config import get_llm
from app.models.schemas import ScoredFlightOffer

_SYSTEM_PROMPT = """You explain why one flight offer ranks where it does compared to another, \
for a traveler comparing flight deals. You are explaining a ranking that has ALREADY been \
computed by a separate scoring system — you are not ranking or scoring anything yourself, \
only explaining the numbers you're given in plain, natural language.

Be concise: 1-2 sentences. Mention the most decision-relevant difference(s) — usually price \
and layovers/duration are what travelers care about most, with cabin class and departure time \
as secondary factors. Don't just restate the numbers ("price is 0.85, layover is 0.7") — \
translate them into what they mean for the traveler ("a bit pricier, but no layover").

Do not invent any facts not present in the data given to you. Do not mention "scores" or \
"scoring" explicitly — speak the way a knowledgeable friend would, not like a system reporting \
its internals."""

_COMPARISON_PROMPT = """Compare these two flights for a traveler. The first is ranked higher \
than the second by an objective scoring system — explain why, in 1-2 sentences.

Higher-ranked flight:
- Price: {higher_price} {currency}
- Stops: {higher_stops}
- Total duration: {higher_duration} minutes
- Cabin: {higher_cabin}
- Departs: {higher_departure_band}

Lower-ranked flight (being compared against):
- Price: {lower_price} {currency}
- Stops: {lower_stops}
- Total duration: {lower_duration} minutes
- Cabin: {lower_cabin}
- Departs: {lower_departure_band}
"""

_STANDALONE_PROMPT = """This flight is the top-ranked result for the traveler's search. \
Describe in 1 sentence why it's a strong option, based on this data:
- Price: {price} {currency}
- Stops: {stops}
- Total duration: {duration} minutes
- Cabin: {cabin}
- Departs: {departure_band}
"""


def _build_chain(human_template: str):
    llm = get_llm(temperature=0.4)  # some warmth/variation in phrasing is fine here, unlike parsing
    prompt = ChatPromptTemplate.from_messages(
        [("system", _SYSTEM_PROMPT), ("human", human_template)]
    )
    return prompt | llm


def _explain_standalone(scored: ScoredFlightOffer) -> str:
    chain = _build_chain(_STANDALONE_PROMPT)
    response = chain.invoke(
        {
            "price": scored.offer.total_amount,
            "currency": scored.offer.total_currency,
            "stops": scored.offer.total_layover_count,
            "duration": scored.offer.total_duration_minutes,
            "cabin": scored.offer.cabin_class.value,
            "departure_band": scored.offer.departure_time_band.value,
        }
    )
    return response.content.strip()


def _explain_comparison(
    higher: ScoredFlightOffer, lower: ScoredFlightOffer
) -> str:
    chain = _build_chain(_COMPARISON_PROMPT)
    response = chain.invoke(
        {
            "higher_price": higher.offer.total_amount,
            "lower_price": lower.offer.total_amount,
            "currency": higher.offer.total_currency,
            "higher_stops": higher.offer.total_layover_count,
            "lower_stops": lower.offer.total_layover_count,
            "higher_duration": higher.offer.total_duration_minutes,
            "lower_duration": lower.offer.total_duration_minutes,
            "higher_cabin": higher.offer.cabin_class.value,
            "lower_cabin": lower.offer.cabin_class.value,
            "higher_departure_band": higher.offer.departure_time_band.value,
            "lower_departure_band": lower.offer.departure_time_band.value,
        }
    )
    return response.content.strip()


@tool
def explain_top_flights_tool(
    scored_offers: list[ScoredFlightOffer], top_n: int = 5
) -> list[ScoredFlightOffer]:
    """Generate plain-English explanations for why the top-ranked flight offers
    scored the way they did, comparing each to the one ranked above it. Only
    the top `top_n` offers receive an explanation; the rest are returned
    unchanged. Does not alter scores or rankings — only adds prose explaining
    an already-computed ranking."""
    top_offers = scored_offers[:top_n]

    explained: list[ScoredFlightOffer] = []
    for i, scored in enumerate(top_offers):
        if i == 0:
            explanation = _explain_standalone(scored)
        else:
            explanation = _explain_comparison(higher=top_offers[i - 1], lower=scored)

        scored.score.explanation = explanation
        explained.append(scored)

    # Any offers beyond top_n are returned unexplained (explanation stays
    # None) rather than dropped — the caller may still want the full
    # ranked list for display, just without prose for every single one.
    return explained + scored_offers[top_n:]
