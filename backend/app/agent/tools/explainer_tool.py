import os
from typing import List
from app.models.schemas import FlightOffer, UserPreferences
from app.config import settings

def generate_tradeoff_explanations(offers: List[FlightOffer], preferences: UserPreferences) -> List[FlightOffer]:
    """
    Tool 3: Generates natural language explanations of trade-offs for each flight offer.
    Supports LLM API calls with fallback to deterministic heuristic explanations.
    """
    if not offers:
        return []

    min_price = min(o.total_amount for o in offers)
    min_dur = min(o.total_duration_minutes for o in offers)

    for offer in offers:
        # Check if LLM integration is available
        llm_explanation = None
        if settings.OPENAI_API_KEY or settings.GROQ_API_KEY:
            llm_explanation = _call_llm_explainer(offer, min_price, min_dur, preferences)

        if not llm_explanation:
            llm_explanation = _generate_heuristic_explanation(offer, min_price, min_dur, preferences)

        offer.tradeoff_explanation = llm_explanation

    return offers

def _generate_heuristic_explanation(offer: FlightOffer, min_price: float, min_dur: int, prefs: UserPreferences) -> str:
    parts = []
    
    # Price analysis
    if offer.total_amount == min_price:
        parts.append(f"Lowest price in results at ${offer.total_amount:.0f}.")
    else:
        diff = offer.total_amount - min_price
        parts.append(f"Costs ${diff:.0f} more than the cheapest option.")

    # Duration and Layovers
    if offer.total_layovers == 0:
        parts.append("Offers a hassle-free non-stop journey.")
    else:
        dur_diff_hrs = (offer.total_duration_minutes - min_dur) / 60.0
        if dur_diff_hrs > 0.1:
            parts.append(f"Includes {offer.total_layovers} layover(s), adding ~{dur_diff_hrs:.1f}h total travel time.")
        else:
            parts.append(f"Includes {offer.total_layovers} layover(s) with minimal extra transit time.")

    # Alignment with preferences
    if prefs.price_weight >= 0.5 and offer.score_breakdown and offer.score_breakdown.price_score > 80:
        parts.append("Great alignment with your budget priority.")
    elif prefs.speed_weight >= 0.5 and offer.score_breakdown and offer.score_breakdown.duration_score > 80:
        parts.append("Excellent alignment with your fast travel request.")

    return " ".join(parts)

def _call_llm_explainer(offer: FlightOffer, min_price: float, min_dur: int, prefs: UserPreferences) -> str:
    # Optional LLM integration hook using requests
    try:
        import requests
        api_key = settings.OPENAI_API_KEY or settings.GROQ_API_KEY
        url = "https://api.openai.com/v1/chat/completions" if settings.OPENAI_API_KEY else "https://api.groq.com/openai/v1/chat/completions"
        model = "gpt-3.5-turbo" if settings.OPENAI_API_KEY else "llama3-8b-8192"
        
        prompt = f"""Summarize flight trade-offs in 2 concise sentences for a user.
Flight details: Airline={offer.airline_name}, Price=${offer.total_amount}, Layovers={offer.total_layovers}, Duration={offer.total_duration_minutes}m.
Lowest Price available=${min_price}, Fastest Duration available={min_dur}m."""
        
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 80,
            "temperature": 0.5
        }
        res = requests.post(url, json=payload, headers=headers, timeout=3)
        if res.status_code == 200:
            return res.json()["choices"][0]["message"]["content"].strip()
    except Exception:
        pass
    return None
