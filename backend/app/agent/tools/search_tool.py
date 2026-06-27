from typing import List
from app.core.duffel_client import duffel_client
from app.core.normalizer import normalize_duffel_offer
from app.models.schemas import FlightOffer

def run_flight_search(origin: str, destination: str, departure_date: str, passengers: int = 1, cabin_class: str = "economy") -> List[FlightOffer]:
    """
    Tool 1: Queries Duffel (or mock engine) for flight offers and normalizes raw payloads.
    """
    raw_offers = duffel_client.search_offers(
        origin=origin,
        destination=destination,
        departure_date=departure_date,
        passengers=passengers,
        cabin_class=cabin_class
    )
    normalized = [normalize_duffel_offer(raw) for raw in raw_offers]
    return normalized
