from __future__ import annotations

from app.models.enums import CabinClass, DepartureTimeBand
from app.models.schemas import FlightOffer, FlightOfferScore, ScoringWeights

# --- Price scoring ---------------------------------------------------------

_PRICE_OUTLIER_PERCENTILE = 0.95

# NOTE: the price-decay steepness used to be a fixed module constant here.
# It's now ScoringWeights.price_sensitivity, a per-search tunable — see the
# docstring on ScoringWeights in models/schemas.py for the full reasoning
# (real flight data showed a fixed steep default let price dominate
# rankings and undercut the multi-criteria tradeoff this project exists to
# demonstrate). Kept as a parameter to _score_price below rather than a
# module-level constant.


def _percentile(values: list[float], percentile: float) -> float:
    if not values:
        raise ValueError("Cannot compute a percentile of an empty list")
    sorted_values = sorted(values)
    if len(sorted_values) == 1:
        return sorted_values[0]
    index = percentile * (len(sorted_values) - 1)
    lower_index = int(index)
    upper_index = min(lower_index + 1, len(sorted_values) - 1)
    fraction = index - lower_index
    return sorted_values[lower_index] + fraction * (
        sorted_values[upper_index] - sorted_values[lower_index]
    )


def _clip_price_outliers(prices: list[float]) -> list[float]:
    if len(prices) < 5:
        # Too few offers for a percentile to be meaningful; skip clipping.
        return prices
    cap = _percentile(prices, _PRICE_OUTLIER_PERCENTILE)
    return [min(p, cap) for p in prices]


def _score_price(price: float, cheapest_price: float, price_sensitivity: float) -> float:
    if cheapest_price <= 0:
        raise ValueError(f"cheapest_price must be positive, got {cheapest_price}")
    if price_sensitivity <= 0:
        raise ValueError(f"price_sensitivity must be positive, got {price_sensitivity}")
    markup_fraction = max(price - cheapest_price, 0) / cheapest_price
    return 1 / (1 + markup_fraction / price_sensitivity)


# --- Layover scoring --------------------------------------------------------

# Base score by stop count, before any duration adjustment. Deliberately
# non-linear: 0->1 stop costs 0.15, but 1->2 stops costs 0.35 — more than
# double the penalty — because most travelers care much more about an
# additional connection than about layover length within one connection.
_LAYOVER_COUNT_BASE_SCORE = {
    0: 1.00,
    1: 0.85,
    2: 0.50,
    3: 0.25,
}
_LAYOVER_COUNT_BASE_SCORE_BEYOND_3 = 0.10

# A layover under this many minutes is treated as the "ideal" connection
# length (long enough to be safe, short enough not to waste the day) and
# gets no duration penalty at all. Above it, score decays gradually.
_IDEAL_LAYOVER_MINUTES = 90
_LAYOVER_DURATION_PENALTY_SCALE = 240  # minutes; controls decay steepness


def _score_layovers(layover_count: int, total_layover_duration_minutes: int) -> float:
    if layover_count == 0:
        return 1.0

    base = _LAYOVER_COUNT_BASE_SCORE.get(
        layover_count, _LAYOVER_COUNT_BASE_SCORE_BEYOND_3
    )

    excess_minutes = max(total_layover_duration_minutes - _IDEAL_LAYOVER_MINUTES, 0)
    duration_penalty_fraction = excess_minutes / (
        excess_minutes + _LAYOVER_DURATION_PENALTY_SCALE
    )

    # Duration penalty can shave off up to ~30% of the base score, but never
    # pushes the score below 0 and never lets a long layover make a 1-stop
    # itinerary score worse than a 2-stop one with a short layover — stop
    # count remains the dominant factor, duration is a fine-tuning input.
    return base * (1 - 0.3 * duration_penalty_fraction)


# --- Comfort scoring ---------------------------------------------------------

_CABIN_CLASS_SCORE = {
    CabinClass.ECONOMY: 0.4,
    CabinClass.PREMIUM_ECONOMY: 0.65,
    CabinClass.BUSINESS: 0.9,
    CabinClass.FIRST: 1.0,
}

_DEPARTURE_TIME_SCORE = {
    DepartureTimeBand.DAYTIME: 1.0,
    DepartureTimeBand.EVENING: 0.8,
    DepartureTimeBand.EARLY_MORNING: 0.6,
    DepartureTimeBand.LATE_NIGHT: 0.4,
    DepartureTimeBand.RED_EYE: 0.3,
}

# Trip duration's contribution to comfort decays smoothly past this many
# minutes — short trips don't get a comfort bonus for being short, but very
# long total-trip durations (lots of time in transit) reduce comfort.
_DURATION_COMFORT_FULL_SCORE_CEILING_MINUTES = 360  # 6 hours
_DURATION_COMFORT_PENALTY_SCALE = 480  # minutes

# Weights for combining the three comfort sub-factors. Cabin class
# dominates (it's the most direct comfort signal), departure time and trip
# duration are secondary contributors.
_COMFORT_SUBWEIGHTS = {"cabin": 0.5, "departure_time": 0.25, "duration": 0.25}


def _score_duration_component(total_duration_minutes: int) -> float:
    if total_duration_minutes <= _DURATION_COMFORT_FULL_SCORE_CEILING_MINUTES:
        return 1.0
    excess = total_duration_minutes - _DURATION_COMFORT_FULL_SCORE_CEILING_MINUTES
    return _DURATION_COMFORT_PENALTY_SCALE / (excess + _DURATION_COMFORT_PENALTY_SCALE)


def _score_comfort(offer: FlightOffer) -> float:
    cabin_score = _CABIN_CLASS_SCORE[offer.cabin_class]
    departure_score = _DEPARTURE_TIME_SCORE[offer.departure_time_band]
    duration_score = _score_duration_component(offer.total_duration_minutes)

    return (
        _COMFORT_SUBWEIGHTS["cabin"] * cabin_score
        + _COMFORT_SUBWEIGHTS["departure_time"] * departure_score
        + _COMFORT_SUBWEIGHTS["duration"] * duration_score
    )


# --- Public entry points ----------------------------------------------------


def score_offers(
    offers: list[FlightOffer], weights: ScoringWeights | None = None
) -> list[FlightOfferScore]:
    if not offers:
        raise ValueError("Cannot score an empty list of offers")

    weights = weights or ScoringWeights()
    _validate_weights(weights)

    raw_prices = [o.total_amount for o in offers]
    clipped_prices = _clip_price_outliers(raw_prices)
    cheapest_price = min(clipped_prices)

    scores: list[FlightOfferScore] = []
    for offer, clipped_price in zip(offers, clipped_prices):
        price_score = _score_price(
            clipped_price, cheapest_price, weights.price_sensitivity
        )
        layover_score = _score_layovers(
            offer.total_layover_count, offer.total_layover_duration_minutes
        )
        comfort_score = _score_comfort(offer)

        overall_score = (
            weights.price_weight * price_score
            + weights.layover_weight * layover_score
            + weights.comfort_weight * comfort_score
        )

        scores.append(
            FlightOfferScore(
                offer_id=offer.offer_id,
                price_score=round(price_score, 4),
                layover_score=round(layover_score, 4),
                comfort_score=round(comfort_score, 4),
                overall_score=round(overall_score, 4),
            )
        )

    return scores


def _validate_weights(weights: ScoringWeights) -> None:
    total = weights.price_weight + weights.layover_weight + weights.comfort_weight
    if abs(total - 1.0) > 1e-6:
        raise ValueError(
            f"ScoringWeights must sum to 1.0, got {total} "
            f"(price={weights.price_weight}, layover={weights.layover_weight}, "
            f"comfort={weights.comfort_weight})"
        )