from typing import List
from app.core.scoring import score_flight_offers
from app.models.schemas import FlightOffer, UserPreferences

def run_flight_scoring(offers: List[FlightOffer], preferences: UserPreferences) -> List[FlightOffer]:
    """
    Tool 2: Evaluates utility scores and ranks flight offers based on dynamic user preferences.
    """
    return score_flight_offers(offers, preferences)
