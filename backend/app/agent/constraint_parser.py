import re
from typing import Dict, Any, Optional
from app.models.schemas import UserPreferences
from app.models.enums import LayoverTolerance

def parse_natural_language_query(query: Optional[str]) -> Dict[str, Any]:
    """
    Parses a natural language search query to extract structured parameters and user preference weights.
    Uses regex and keyword heuristics, designed to work seamlessly with or without LLM calls.
    """
    extracted = {
        "preferences": UserPreferences(),
        "extracted_keywords": []
    }
    if not query:
        return extracted

    q_lower = query.lower()
    prefs = UserPreferences(price_weight=0.33, speed_weight=0.33, comfort_weight=0.34)
    keywords = []

    # Detect budget / price sensitivity
    if re.search(r'\b(cheap|cheapest|budget|low cost|affordable|inexpensive|saving|save money)\b', q_lower):
        prefs.price_weight = 0.60
        prefs.speed_weight = 0.20
        prefs.comfort_weight = 0.20
        keywords.append("Budget Priority")

    # Detect speed / duration sensitivity
    if re.search(r'\b(fast|fastest|quick|quickest|shortest|direct|no layover|speedy)\b', q_lower):
        prefs.speed_weight = 0.60
        prefs.price_weight = 0.20
        prefs.comfort_weight = 0.20
        keywords.append("Speed Priority")

    # Detect comfort / luxury sensitivity
    if re.search(r'\b(comfort|comfortable|legroom|luxury|business|first class|relaxing|convenient)\b', q_lower):
        prefs.comfort_weight = 0.60
        prefs.price_weight = 0.20
        prefs.speed_weight = 0.20
        keywords.append("Comfort Priority")

    # Detect Layover tolerances
    if re.search(r'\b(nonstop|non-stop|direct only|no layovers)\b', q_lower):
        prefs.layover_tolerance = LayoverTolerance.DIRECT_ONLY
        keywords.append("Non-stop Only")
    elif re.search(r'\b(max 1 layover|at most 1 layover|one layover|1 stop)\b', q_lower):
        prefs.layover_tolerance = LayoverTolerance.MAX_ONE
        keywords.append("Max 1 Layover")

    # Detect preferred time of day
    if re.search(r'\b(morning|early|dawn)\b', q_lower):
        prefs.preferred_departure_time = "morning"
        keywords.append("Morning Departure")
    elif re.search(r'\b(afternoon|midday)\b', q_lower):
        prefs.preferred_departure_time = "afternoon"
        keywords.append("Afternoon Departure")
    elif re.search(r'\b(evening|night|late|overnight)\b', q_lower):
        prefs.preferred_departure_time = "evening"
        keywords.append("Evening Departure")

    # Detect max price constraint e.g. "under $800" or "under 500"
    price_match = re.search(r'under\s*\$?(\d+)', q_lower) or re.search(r'less than\s*\$?(\d+)', q_lower) or re.search(r'\$?(\d+)\s*budget', q_lower)
    if price_match:
        prefs.max_price = float(price_match.group(1))
        keywords.append(f"Max Price: ${prefs.max_price}")

    extracted["preferences"] = prefs
    extracted["extracted_keywords"] = keywords
    return extracted
