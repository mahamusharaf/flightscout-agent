from __future__ import annotations

import os
from dotenv import load_dotenv

load_dotenv()

from langchain_groq import ChatGroq

DUFFEL_TEST_TOKEN = os.environ.get("DUFFEL_TEST_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# Model used for BOTH constraint parsing and explanation generation for now.
# Constraint parsing is a structured-extraction task that smaller/faster
# models handle well. Explanation generation is the actual showpiece of the
# demo and is more sensitive to model quality — if real output (tested via
# check_explainer_e2e.py) comes back flat or generic, this is the line to
# change, ideally to a separate EXPLAINER_MODEL constant rather than
# upgrading both jobs at once.
DEFAULT_MODEL_NAME = "llama-3.3-70b-versatile"


def get_llm(temperature: float = 0.0, model_name: str | None = None) -> ChatGroq:
    if not GROQ_API_KEY:
        raise ValueError(
            "GROQ_API_KEY environment variable not set. Get a key at "
            "https://console.groq.com and export it before running the agent."
        )

    return ChatGroq(
        model=model_name or DEFAULT_MODEL_NAME,
        temperature=temperature,
        api_key=GROQ_API_KEY,
    )