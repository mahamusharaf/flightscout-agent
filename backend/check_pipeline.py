"""
End-to-end check of duffel_client -> normalizer -> scoring, against the
live API. Validates that scoring.py produces sane, well-ranked results on
real data — including the known price outlier (~€10,053) from earlier
testing, to confirm outlier clipping is doing its job.

Usage:
    export DUFFEL_TEST_TOKEN=duffel_test_xxxxx
    python check_scoring_e2e.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.duffel_client import DuffelClient, DuffelClientError
from app.core.normalizer import normalize_offers
from app.core.scoring import score_offers

if not os.environ.get("DUFFEL_TEST_TOKEN"):
    print("Set DUFFEL_TEST_TOKEN environment variable first.")
    sys.exit(1)

client = DuffelClient()

print("Calling live Duffel API (JFK -> LAX, 2026-08-15)...")
try:
    raw_offers = client.search_offers(
        origin_iata="JFK", destination_iata="LAX", departure_date="2026-08-15"
    )
except DuffelClientError as e:
    print(f"Duffel API call failed: status={e.status_code}")
    print(e.body)
    sys.exit(1)

offers = normalize_offers(raw_offers)
print(f"Normalized: {len(offers)} offers")

scores = score_offers(offers)
print(f"Scored: {len(scores)} offers")

# Pair offers with their scores and sort by overall_score descending —
# this is the actual ranked output a user would see.
offer_by_id = {o.offer_id: o for o in offers}
ranked = sorted(scores, key=lambda s: s.overall_score, reverse=True)

print("\n--- Top 10 ranked offers ---")
print(f"{'Rank':<5}{'Price':<10}{'Stops':<7}{'DurMin':<8}{'Cabin':<10}{'Departs':<14}{'Overall':<9}{'P/L/C breakdown'}")
for i, score in enumerate(ranked[:10], start=1):
    offer = offer_by_id[score.offer_id]
    print(
        f"{i:<5}"
        f"{offer.total_amount:<10.2f}"
        f"{offer.total_layover_count:<7}"
        f"{offer.total_duration_minutes:<8}"
        f"{offer.cabin_class.value:<10}"
        f"{offer.departure_time_band.value:<14}"
        f"{score.overall_score:<9.4f}"
        f"{score.price_score:.2f}/{score.layover_score:.2f}/{score.comfort_score:.2f}"
    )

print("\n--- Bottom 5 ranked offers ---")
for i, score in enumerate(ranked[-5:], start=len(ranked) - 4):
    offer = offer_by_id[score.offer_id]
    print(
        f"{i:<5}"
        f"{offer.total_amount:<10.2f}"
        f"{offer.total_layover_count:<7}"
        f"{offer.total_duration_minutes:<8}"
        f"{offer.cabin_class.value:<10}"
        f"{offer.departure_time_band.value:<14}"
        f"{score.overall_score:<9.4f}"
        f"{score.price_score:.2f}/{score.layover_score:.2f}/{score.comfort_score:.2f}"
    )

# Specifically locate and print the known price outlier to confirm it
# didn't break the price scoring for everyone else, and to see how IT
# scored (should be low on price, but not so low it breaks the formula).
print("\n--- Outlier check (most expensive offer) ---")
most_expensive = max(offers, key=lambda o: o.total_amount)
outlier_score = next(s for s in scores if s.offer_id == most_expensive.offer_id)
print(
    f"Most expensive offer: {most_expensive.total_amount:.2f} "
    f"{most_expensive.total_currency}, "
    f"price_score={outlier_score.price_score}, "
    f"overall_score={outlier_score.overall_score}"
)

cheapest = min(offers, key=lambda o: o.total_amount)
cheapest_score = next(s for s in scores if s.offer_id == cheapest.offer_id)
print(
    f"Cheapest offer: {cheapest.total_amount:.2f} {cheapest.total_currency}, "
    f"price_score={cheapest_score.price_score}, "
    f"overall_score={cheapest_score.overall_score}"
)

# Sanity check: is a normal mid-priced offer's price_score reasonably high,
# or did the outlier still drag it down? This is the actual question we
# need answered to trust the clipping logic.
mid_priced_offers = sorted(offers, key=lambda o: o.total_amount)
median_offer = mid_priced_offers[len(mid_priced_offers) // 2]
median_score = next(s for s in scores if s.offer_id == median_offer.offer_id)
print(
    f"Median-priced offer: {median_offer.total_amount:.2f} "
    f"{median_offer.total_currency}, price_score={median_score.price_score}"
)

print("\nSCORING E2E CHECK COMPLETE")