import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "FlightScout API"
    API_V1_STR: str = "/api"
    DUFFEL_API_TOKEN: str = os.getenv("DUFFEL_API_TOKEN", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    DEFAULT_CURRENCY: str = "USD"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
