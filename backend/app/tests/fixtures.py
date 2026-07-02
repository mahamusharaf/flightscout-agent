RAW_OFFER_NONSTOP = {
    "id": "off_0000B7lq9RtkjCZRpnNsb9",
    "total_amount": "168.52",
    "total_currency": "EUR",
    "expires_at": "2026-06-27T21:43:33.643303Z",
    "owner": {"iata_code": "AA", "name": "American Airlines"},
    "slices": [
        {
            "origin": {"iata_code": "JFK"},
            "destination": {"iata_code": "LAX"},
            "duration": "PT5H52M",
            "segments": [
                {
                    "origin": {"iata_code": "JFK"},
                    "destination": {"iata_code": "LAX"},
                    "departing_at": "2026-08-15T10:50:00",
                    "arriving_at": "2026-08-15T13:42:00",
                    "duration": "PT5H52M",
                    "operating_carrier": {"iata_code": "AA", "name": "American Airlines"},
                    "marketing_carrier_flight_number": "10",
                    "passengers": [{"cabin_class": "economy"}],
                }
            ],
        }
    ],
}

RAW_OFFER_ONE_STOP = {
    "id": "off_0000B7lqAS_onestop",
    "total_amount": "213.46",
    "total_currency": "EUR",
    "expires_at": "2026-06-27T21:43:33.643303Z",
    "owner": {"iata_code": "AS", "name": "Alaska Airlines"},
    "slices": [
        {
            "origin": {"iata_code": "JFK"},
            "destination": {"iata_code": "LAX"},
            "duration": "PT9H48M",
            "segments": [
                {
                    "origin": {"iata_code": "JFK"},
                    "destination": {"iata_code": "SEA"},
                    "departing_at": "2026-08-15T23:30:00",
                    "arriving_at": "2026-08-16T02:00:00",
                    "duration": "PT6H25M",  # note: includes timezone shift in real data; kept simple here
                    "operating_carrier": {"iata_code": "AS", "name": "Alaska Airlines"},
                    "marketing_carrier_flight_number": "401",
                    "passengers": [{"cabin_class": "economy"}],
                },
                {
                    "origin": {"iata_code": "SEA"},
                    "destination": {"iata_code": "LAX"},
                    "departing_at": "2026-08-16T03:30:00",
                    "arriving_at": "2026-08-16T05:50:00",
                    "duration": "PT2H20M",
                    "operating_carrier": {"iata_code": "AS", "name": "Alaska Airlines"},
                    "marketing_carrier_flight_number": "405",
                    "passengers": [{"cabin_class": "economy"}],
                },
            ],
        }
    ],
}

RAW_OFFER_MALFORMED = {
    "id": "off_malformed_missing_total_amount",
    # total_amount deliberately missing to test that normalize_offers skips
    # this gracefully rather than crashing the whole batch
    "total_currency": "EUR",
    "owner": {"iata_code": "ZZ", "name": "Duffel Airways"},
    "slices": [
        {
            "origin": {"iata_code": "JFK"},
            "destination": {"iata_code": "LAX"},
            "duration": "PT6H00M",
            "segments": [
                {
                    "origin": {"iata_code": "JFK"},
                    "destination": {"iata_code": "LAX"},
                    "departing_at": "2026-08-15T09:00:00",
                    "arriving_at": "2026-08-15T15:00:00",
                    "duration": "PT6H00M",
                    "operating_carrier": {"iata_code": "ZZ", "name": "Duffel Airways"},
                    "marketing_carrier_flight_number": "1",
                    "passengers": [{"cabin_class": "economy"}],
                }
            ],
        }
    ],
}