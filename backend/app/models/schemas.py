"""
Internal data schemas for FlightScout.

Design principle: Duffel's offer/slice/segment schema is detailed but
provider-specific. Nothing downstream of normalizer.py should ever touch a
raw Duffel response directly — scoring.py, the agent tools, and the API
routes all operate on these internal models instead. That's what makes it
possible to swap or add a second flight data provider later without
touching scoring logic.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.enums import CabinClass, DepartureTimeBand, OfferSource


class FlightSegment(BaseModel):
    """
    One physical flight (a single takeoff and landing) within a slice.
    A non-stop trip has exactly one segment per slice; a 1-stop trip has two.
    """

    origin_iata: str = Field(..., description="3-letter IATA code, e.g. 'JFK'")
    destination_iata: str
    departure_at: datetime
    arrival_at: datetime
    airline_iata: str = Field(..., description="2-letter airline code, e.g. 'BA'")
    airline_name: str
    flight_number: str
    duration_minutes: int = Field(..., description="Duration of this segment alone")


class FlightSlice(BaseModel):
    """
    One leg of the overall journey (e.g. outbound, or return). Contains one
    or more segments if there are layovers within that leg.
    """

    origin_iata: str
    destination_iata: str
    segments: list[FlightSegment]
    duration_minutes: int = Field(
        ..., description="Total duration of this slice including layover time"
    )

    @property
    def layover_count(self) -> int:
        return max(len(self.segments) - 1, 0)

    @property
    def layover_duration_minutes(self) -> int:
        """
        Total time spent on the ground between segments within this slice.
        Computed as slice duration minus the sum of segment flight times.
        """
        flight_time = sum(s.duration_minutes for s in self.segments)
        return max(self.duration_minutes - flight_time, 0)


class FlightOffer(BaseModel):
    """
    The internal, provider-agnostic representation of a single bookable
    flight offer. This is what scoring.py, the explainer tool, and the
    frontend all consume.
    """

    offer_id: str = Field(..., description="Provider's offer ID, used to re-fetch/book")
    source: OfferSource = OfferSource.DUFFEL

    slices: list[FlightSlice]
    cabin_class: CabinClass

    total_amount: float
    total_currency: str = Field(..., description="ISO 4217 code, e.g. 'USD'")

    # Pre-computed convenience fields, derived once at normalization time so
    # scoring.py doesn't need to recompute them from nested slices on every
    # call. Kept here rather than as @property so they can be cached and
    # serialized straight to the frontend without re-deriving anything.
    total_duration_minutes: int = Field(
        ..., description="Sum of all slice durations, including all layovers"
    )
    total_layover_count: int = Field(
        ..., description="Sum of layover_count across all slices"
    )
    total_layover_duration_minutes: int = Field(
        ..., description="Sum of layover_duration_minutes across all slices"
    )
    departure_time_band: DepartureTimeBand = Field(
        ..., description="Bucketed departure time of the first segment, used in comfort scoring"
    )

    expires_at: Optional[datetime] = Field(
        None, description="When this offer's price is no longer guaranteed (Duffel offers go stale)"
    )


class FlightOfferScore(BaseModel):
    """
    Score breakdown for a single offer, produced by scoring.py. Kept as a
    separate model from FlightOffer (rather than bolting score fields onto
    FlightOffer directly) so the deterministic scoring layer has a clean
    output type that's easy to unit test in isolation.
    """

    offer_id: str
    price_score: float = Field(..., ge=0, le=1)
    layover_score: float = Field(..., ge=0, le=1)
    comfort_score: float = Field(..., ge=0, le=1)
    overall_score: float = Field(..., ge=0, le=1)

    # Explanation is filled in later by the explainer tool (LLM), so it's
    # optional here — scoring.py never sets this field itself.
    explanation: Optional[str] = None


class ScoredFlightOffer(BaseModel):
    """
    Convenience composite of an offer plus its score, for handing back to
    the frontend in one object instead of two parallel lists.
    """

    offer: FlightOffer
    score: FlightOfferScore


class ScoringWeights(BaseModel):
    """
    Weights for the three scoring components, plus price_sensitivity which
    controls how steeply price_score decays as an offer's price rises above
    the cheapest in the batch.

    price_weight/layover_weight/comfort_weight are exposed as a model
    (rather than hardcoded constants in scoring.py) so the agent can adjust
    weights based on user-stated preferences, e.g. someone who says "I
    really don't care about comfort, just find me something cheap" should
    be able to shift weight toward price_weight without touching
    scoring.py's code.

    price_sensitivity is a separate knob from price_weight: price_weight
    controls how much price matters *relative to layovers and comfort* in
    the final blend, while price_sensitivity controls the *shape* of the
    price scoring curve itself — how harshly a given percentage markup
    over the cheapest offer gets penalized, independent of how much price
    matters overall. A budget-conscious traveler wants both price_weight
    and price_sensitivity high (price matters a lot, and even small
    markups hurt); someone optimizing primarily for comfort or fewer
    layovers wants price_weight low but might still want price_sensitivity
    moderate so price isn't a complete non-factor once price_weight kicks in.

    Concretely: price_sensitivity is the "half-life" markup fraction at
    which price_score drops to 0.5. A LOWER value means a steeper, more
    punishing curve (e.g. 0.5 -> a 50% markup over the cheapest offer
    already scores 0.5). A HIGHER value is gentler (e.g. 1.0 -> it takes a
    100% markup to reach the same 0.5 score). Defaults to 1.0 (gentler),
    chosen after testing against real flight data showed many reasonable
    1-stop offers sitting 90-150% above the cheapest direct flight — a
    steeper default would let price alone dominate rankings and undercut
    the project's actual purpose: showcasing a genuine price/layover/
    comfort tradeoff rather than a price sort with extra steps.

    Must sum to 1.0 across the three *_weight fields — scoring.py validates
    this at call time. price_sensitivity is independent and not part of
    that sum.
    """

    price_weight: float = 0.5
    layover_weight: float = 0.3
    comfort_weight: float = 0.2
    price_sensitivity: float = 1.0


class SearchRequest(BaseModel):
    """
    Incoming request shape for POST /search. This is the structured form;
    the agent's constraint_parser.py is responsible for producing this from
    a natural-language query before search_tool.py is invoked.
    """

    origin_iata: str
    destination_iata: str
    departure_date: str = Field(..., description="YYYY-MM-DD")
    return_date: Optional[str] = Field(None, description="YYYY-MM-DD, omit for one-way")
    cabin_class: CabinClass = CabinClass.ECONOMY
    adults: int = 1

    max_budget: Optional[float] = None
    weights: Optional[ScoringWeights] = None


class SearchResponse(BaseModel):
    """
    Final response shape for POST /search: ranked, scored offers plus the
    natural-language query that was parsed (echoed back for UI display).
    """

    query: str
    parsed_request: SearchRequest
    results: list[ScoredFlightOffer]