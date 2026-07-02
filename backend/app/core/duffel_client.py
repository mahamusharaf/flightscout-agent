from __future__ import annotations

import os
from typing import Optional

import requests

DUFFEL_BASE_URL = "https://api.duffel.com"
DUFFEL_API_VERSION = "v2"


class DuffelClientError(Exception):
    def __init__(self, status_code: int, body: dict):
        self.status_code = status_code
        self.body = body
        super().__init__(f"Duffel API error {status_code}: {body}")


class DuffelClient:
    def __init__(self, api_token: Optional[str] = None):
        self.api_token = api_token or os.environ.get("DUFFEL_TEST_TOKEN")
        if not self.api_token:
            raise ValueError(
                "Duffel API token not found. Set the DUFFEL_TEST_TOKEN "
                "environment variable or pass api_token explicitly."
            )

        self._headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Duffel-Version": DUFFEL_API_VERSION,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def search_offers(
        self,
        origin_iata: str,
        destination_iata: str,
        departure_date: str,
        return_date: Optional[str] = None,
        cabin_class: str = "economy",
        adults: int = 1,
    ) -> list[dict]:
        slices = [
            {
                "origin": origin_iata,
                "destination": destination_iata,
                "departure_date": departure_date,
            }
        ]
        if return_date:
            slices.append(
                {
                    "origin": destination_iata,
                    "destination": origin_iata,
                    "departure_date": return_date,
                }
            )

        payload = {
            "data": {
                "slices": slices,
                "passengers": [{"type": "adult"} for _ in range(adults)],
                "cabin_class": cabin_class,
            }
        }

        response = requests.post(
            f"{DUFFEL_BASE_URL}/air/offer_requests",
            headers=self._headers,
            json=payload,
            params={"return_offers": "true"},
            timeout=30,
        )

        if response.status_code >= 400:
            try:
                body = response.json()
            except ValueError:
                body = {"raw_text": response.text}
            raise DuffelClientError(response.status_code, body)

        data = response.json()
        return data.get("data", {}).get("offers", [])