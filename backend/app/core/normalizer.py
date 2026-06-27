"""
Transforms raw Duffel offer dicts (as returned by duffel_client.search_offers)
into our internal FlightOffer schema.

This is the ONLY file in the app that should know Duffel's specific JSON
shape (string amounts, ISO 8601 durations, cabin_class nested under
segments[].passengers[]). Everything downstream — scoring.py, the agent
tools, the API routes, the frontend — works exclusively with FlightOffer
objects and never touches a raw Duffel dict.

Confirmed against a real sandbox response (JFK->LAX, 2026-08-15, 56 offers
across ZZ/AA/BA/IB/AS) before writing this, rather than guessing the shape.
"""

from __future__ import annotations

import re
from datetime import datetime

from app.models.enums import CabinClass, DepartureTimeBand, OfferSource
from app.models.schemas import FlightOffer, FlightSegment, FlightSlice

# Matches ISO 8601 durations in the forms Duffel actually uses, e.g.
# "PT5H52M", "PT45M", "PT9H", and — confirmed via a real sandbox response —
# "P1DT7M" for slices/segments spanning past midnight into the next day.
# The day component is optional and sits before the "T"; the whole "T..."
# time portion is itself optional (a bare "P1D" with no time component is
# valid ISO 8601), and hour/minute within it are each optional too.
_ISO_DURATION_RE = re.compile(r"^P(?:(\d+)D)?(?:T(?:(\d+)H)?(?:(\d+)M)?)?$")


def parse_iso_duration_to_minutes(duration: str) -> int:
    """
    Converts an ISO 8601 duration string like "PT5H52M" or "P1DT7M" into
    total minutes. Raises ValueError on a format we don't recognize, rather
    than silently returning 0 — a silent 0-minute duration would corrupt
    scoring without any visible error.
    """
    match = _ISO_DURATION_RE.match(duration)
    if not match or duration == "P":
        raise ValueError(f"Unrecognized ISO 8601 duration format: {duration!r}")

    days_str, hours_str, minutes_str = match.groups()
    days = int(days_str) if days_str else 0
    hours = int(hours_str) if hours_str else 0
    minutes = int(minutes_str) if minutes_str else 0
    return days * 24 * 60 + hours * 60 + minutes


def _bucket_departure_time(departing_at: datetime) -> DepartureTimeBand:
    """
    Buckets a departure datetime into a DepartureTimeBand based on the hour
    component, per the boundaries documented on DepartureTimeBand.

    Note: departing_at from Duffel is local time at the departure airport
    (no UTC offset in the string), so this naturally buckets by local time
    without any timezone conversion needed.
    """
    hour = departing_at.hour
    if 0 <= hour < 5:
        return DepartureTimeBand.RED_EYE
    if 5 <= hour < 8:
        return DepartureTimeBand.EARLY_MORNING
    if 8 <= hour < 19:
        return DepartureTimeBand.DAYTIME
    if 19 <= hour < 23:
        return DepartureTimeBand.EVENING
    return DepartureTimeBand.LATE_NIGHT


def _normalize_segment(raw_segment: dict) -> FlightSegment:
    carrier = raw_segment["operating_carrier"]
    return FlightSegment(
        origin_iata=raw_segment["origin"]["iata_code"],
        destination_iata=raw_segment["destination"]["iata_code"],
        departure_at=raw_segment["departing_at"],
        arrival_at=raw_segment["arriving_at"],
        airline_iata=carrier["iata_code"],
        airline_name=carrier["name"],
        flight_number=raw_segment["marketing_carrier_flight_number"],
        duration_minutes=parse_iso_duration_to_minutes(raw_segment["duration"]),
    )


def _normalize_slice(raw_slice: dict) -> FlightSlice:
    segments = [_normalize_segment(s) for s in raw_slice["segments"]]
    return FlightSlice(
        origin_iata=raw_slice["origin"]["iata_code"],
        destination_iata=raw_slice["destination"]["iata_code"],
        segments=segments,
        duration_minutes=parse_iso_duration_to_minutes(raw_slice["duration"]),
    )


def _extract_cabin_class(raw_offer: dict) -> CabinClass:
    """
    Cabin class isn't a top-level field on the offer — it's nested under
    the first segment's first passenger. For our current single-adult,
    single-cabin-class-per-search use case this is safe; if multi-passenger
    mixed-cabin support is ever needed, this function is where that logic
    would expand.
    """
    first_segment = raw_offer["slices"][0]["segments"][0]
    cabin_value = first_segment["passengers"][0]["cabin_class"]
    return CabinClass(cabin_value)


def normalize_offer(raw_offer: dict) -> FlightOffer:
    """
    Converts a single raw Duffel offer dict into a FlightOffer.

    Raises KeyError/ValueError if the raw offer is missing an expected
    field or has a value we can't parse — deliberately not swallowed here,
    since a malformed offer should surface loudly rather than silently
    produce a FlightOffer with wrong/default data that corrupts scoring.
    """
    slices = [_normalize_slice(s) for s in raw_offer["slices"]]

    total_duration_minutes = sum(s.duration_minutes for s in slices)
    total_layover_count = sum(s.layover_count for s in slices)
    total_layover_duration_minutes = sum(
        s.layover_duration_minutes for s in slices
    )

    first_departure = slices[0].segments[0].departure_at

    return FlightOffer(
        offer_id=raw_offer["id"],
        source=OfferSource.DUFFEL,
        slices=slices,
        cabin_class=_extract_cabin_class(raw_offer),
        total_amount=float(raw_offer["total_amount"]),
        total_currency=raw_offer["total_currency"],
        total_duration_minutes=total_duration_minutes,
        total_layover_count=total_layover_count,
        total_layover_duration_minutes=total_layover_duration_minutes,
        departure_time_band=_bucket_departure_time(first_departure),
        expires_at=raw_offer.get("expires_at"),
    )


def normalize_offers(raw_offers: list[dict]) -> list[FlightOffer]:
    """
    Normalizes a list of raw offers. Offers that fail to parse are skipped
    with their error logged rather than crashing the whole batch — one
    malformed offer out of 56 shouldn't take down the entire search, but
    we also don't want to fail silently with zero visibility, hence the
    print here (swap for proper logging once the app has a logger configured).
    """
    normalized: list[FlightOffer] = []
    for raw_offer in raw_offers:
        try:
            normalized.append(normalize_offer(raw_offer))
        except (KeyError, ValueError) as e:
            offer_id = raw_offer.get("id", "<unknown>")
            print(f"[normalizer] Skipping offer {offer_id}: {e}")
    return normalized