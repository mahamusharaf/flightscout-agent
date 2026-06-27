import pytest
from app.core.normalizer import normalize_duffel_offer

def test_normalize_duffel_offer():
    raw_payload = {
        "id": "off_test_123",
        "total_amount": "550.00",
        "total_currency": "USD",
        "owner": {"name": "Test Airlines", "logo": "https://example.com/logo.png"},
        "cabin_class": "economy",
        "slices": [
            {
                "origin": "JFK",
                "destination": "LHR",
                "duration_minutes": 420,
                "layover_count": 0,
                "segments": [
                    {
                        "id": "seg_1",
                        "origin": "JFK",
                        "destination": "LHR",
                        "departing_at": "2026-07-01T08:00:00",
                        "arriving_at": "2026-07-01T20:00:00",
                        "airline": "Test Airlines",
                        "airline_code": "TA",
                        "flight_number": "TA101",
                        "duration_minutes": 420
                    }
                ]
            }
        ]
    }

    offer = normalize_duffel_offer(raw_payload)
    assert offer.id == "off_test_123"
    assert offer.total_amount == 550.0
    assert offer.currency == "USD"
    assert offer.airline_name == "Test Airlines"
    assert offer.total_duration_minutes == 420
    assert offer.total_layovers == 0
    assert len(offer.slices) == 1
