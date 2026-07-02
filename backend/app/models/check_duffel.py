import json
import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.environ.get("DUFFEL_TEST_TOKEN")
if not TOKEN:
    print("Set DUFFEL_TEST_TOKEN environment variable first.")
    sys.exit(1)

BASE_URL = "https://api.duffel.com"

# Duffel requires this header to pin the API version you're coding against.
# Without it you get routed to whatever the "default" version is, which can
# silently change the response shape later. Using today's stable version.
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Duffel-Version": "v2",
    "Content-Type": "application/json",
    "Accept": "application/json",
}

payload = {
    "data": {
        "slices": [
            {
                "origin": "JFK",
                "destination": "LAX",
                "departure_date": "2026-08-15",
            }
        ],
        "passengers": [{"type": "adult"}],
        "cabin_class": "economy",
    }
}

resp = requests.post(
    f"{BASE_URL}/air/offer_requests",
    headers=HEADERS,
    json=payload,
    # return_offers=true (default) waits for and includes offers inline,
    # rather than requiring a separate fetch.
    params={"return_offers": "true"},
)

print(f"Status: {resp.status_code}")

if resp.status_code >= 400:
    print("ERROR response body:")
    print(json.dumps(resp.json(), indent=2))
    sys.exit(1)

body = resp.json()
offers = body.get("data", {}).get("offers", [])
print(f"Offer request id: {body['data']['id']}")
print(f"Number of offers returned: {len(offers)}")

if offers:
    print("\n--- Airline / cabin_class / duration shape across first 10 offers ---")
    for o in offers[:10]:
        airline = o["owner"]["iata_code"]
        first_slice = o["slices"][0]
        first_seg = first_slice["segments"][0]
        cabin = first_seg["passengers"][0]["cabin_class"]
        seg_duration = first_seg["duration"]
        slice_duration = first_slice["duration"]
        stop_count = len(first_slice["segments"]) - 1
        print(f"{airline:4} | cabin={cabin:10} | seg_dur={seg_duration:10} | slice_dur={slice_duration:10} | stops={stop_count} | total={o['total_amount']} {o['total_currency']}")
else:
    print("No offers returned — Duffel Airways sandbox should still return something for this route/date.")