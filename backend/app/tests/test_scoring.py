import pytest
from app.core.scoring import score_flight_offers
from app.models.schemas import FlightOffer, UserPreferences, FlightSlice, FlightSegment

def test_scoring_boundary_and_ranking():
    offer1 = FlightOffer(
        id="off_cheapest",
        total_amount=300.0,
        currency="USD",
        slices=[],
        total_duration_minutes=600,
        total_layovers=1,
        cabin_class="economy",
        airline_name="BudgetAir"
    )
    offer2 = FlightOffer(
        id="off_fastest",
        total_amount=600.0,
        currency="USD",
        slices=[],
        total_duration_minutes=300,
        total_layovers=0,
        cabin_class="economy",
        airline_name="FastAir"
    )

    # Priority on price
    price_prefs = UserPreferences(price_weight=0.8, speed_weight=0.1, comfort_weight=0.1)
    scored_price = score_flight_offers([offer1, offer2], price_prefs)
    assert scored_price[0].id == "off_cheapest"

    # Priority on speed
    speed_prefs = UserPreferences(price_weight=0.1, speed_weight=0.8, comfort_weight=0.1)
    scored_speed = score_flight_offers([offer1, offer2], speed_prefs)
    assert scored_speed[0].id == "off_fastest"
