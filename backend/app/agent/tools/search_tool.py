from __future__ import annotations

from langchain.tools import tool

from app.core.duffel_client import DuffelClient, DuffelClientError
from app.core.normalizer import normalize_offers
from app.models.schemas import FlightOffer


class FlightSearchError(Exception):
    pass


@tool
def search_flights_tool(
    origin_iata: str,
    destination_iata: str,
    departure_date: str,
    return_date: str | None = None,
    cabin_class: str = "economy",
    adults: int = 1,
) -> list[FlightOffer]:
    client = DuffelClient()
    try:
        raw_offers = client.search_offers(
            origin_iata=origin_iata,
            destination_iata=destination_iata,
            departure_date=departure_date,
            return_date=return_date,
            cabin_class=cabin_class,
            adults=adults,
        )
    except DuffelClientError as e:
        raise FlightSearchError(
            f"Flight search failed (status {e.status_code}): {e.body}"
        ) from e

    offers = normalize_offers(raw_offers)

    if not offers:
        raise FlightSearchError(
            f"No flight offers found for {origin_iata} -> {destination_iata} "
            f"on {departure_date}. The route or date may be invalid, or "
            f"Duffel's sandbox simply has no coverage for it."
        )

    return offers