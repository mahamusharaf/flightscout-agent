from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.enums import CabinClass, DepartureTimeBand, OfferSource


class FlightSegment(BaseModel):

    origin_iata: str = Field(..., description="3-letter IATA code, e.g. 'JFK'")
    destination_iata: str
    departure_at: datetime
    arrival_at: datetime
    airline_iata: str = Field(..., description="2-letter airline code, e.g. 'BA'")
    airline_name: str
    flight_number: str
    duration_minutes: int = Field(..., description="Duration of this segment alone")


class FlightSlice(BaseModel):

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
        flight_time = sum(s.duration_minutes for s in self.segments)
        return max(self.duration_minutes - flight_time, 0)


class FlightOffer(BaseModel):

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

    offer_id: str
    price_score: float = Field(..., ge=0, le=1)
    layover_score: float = Field(..., ge=0, le=1)
    comfort_score: float = Field(..., ge=0, le=1)
    overall_score: float = Field(..., ge=0, le=1)

    # Explanation is filled in later by the explainer tool (LLM), so it's
    # optional here — scoring.py never sets this field itself.
    explanation: Optional[str] = None


class ScoredFlightOffer(BaseModel):

    offer: FlightOffer
    score: FlightOfferScore


class ScoringWeights(BaseModel):

    price_weight: float = 0.5
    layover_weight: float = 0.3
    comfort_weight: float = 0.2
    price_sensitivity: float = 1.0


class SearchRequest(BaseModel):

    origin_iata: str
    destination_iata: str
    departure_date: str = Field(..., description="YYYY-MM-DD")
    return_date: Optional[str] = Field(None, description="YYYY-MM-DD, omit for one-way")
    cabin_class: CabinClass = CabinClass.ECONOMY
    adults: int = 1

    max_budget: Optional[float] = None
    weights: Optional[ScoringWeights] = None


class SearchResponse(BaseModel):

    query: str
    parsed_request: SearchRequest
    results: list[ScoredFlightOffer]