from enum import Enum


class CabinClass(str, Enum):
    ECONOMY = "economy"
    PREMIUM_ECONOMY = "premium_economy"
    BUSINESS = "business"
    FIRST = "first"


class DepartureTimeBand(str, Enum):
    RED_EYE = "red_eye"
    EARLY_MORNING = "early_morning"
    DAYTIME = "daytime"
    EVENING = "evening"
    LATE_NIGHT = "late_night"


class OfferSource(str, Enum):
    DUFFEL = "duffel"