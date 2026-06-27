"""
Enums shared across schemas, scoring, and the agent layer.

Kept separate from schemas.py so scoring.py and the agent tools can import
just the categorical types without pulling in the full Pydantic models.
"""

from enum import Enum


class CabinClass(str, Enum):
    """
    Mirrors Duffel's cabin_class values so we can pass these straight through
    to the Duffel offer request without a translation layer.
    """
    ECONOMY = "economy"
    PREMIUM_ECONOMY = "premium_economy"
    BUSINESS = "business"
    FIRST = "first"


class DepartureTimeBand(str, Enum):
    """
    Coarse buckets for "desirability" of a departure time, used as one input
    into the comfort score. Red-eyes and very early departures score lower;
    standard daytime departures score higher.

    Boundaries (local departure airport time):
      RED_EYE:        00:00 - 04:59
      EARLY_MORNING:  05:00 - 07:59
      DAYTIME:        08:00 - 18:59
      EVENING:        19:00 - 22:59
      LATE_NIGHT:     23:00 - 23:59
    """
    RED_EYE = "red_eye"
    EARLY_MORNING = "early_morning"
    DAYTIME = "daytime"
    EVENING = "evening"
    LATE_NIGHT = "late_night"


class OfferSource(str, Enum):
    """
    Tracks where a normalized offer came from. Currently only Duffel, but
    keeping this as an enum (rather than hardcoding "duffel" as a string
    everywhere) means adding a second provider later doesn't require
    touching every call site that checks the source.
    """
    DUFFEL = "duffel"