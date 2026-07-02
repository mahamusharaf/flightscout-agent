from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import health, search

app = FastAPI(
    title="FlightScout API",
    description="Multi-criteria flight deal search with LLM-explained tradeoffs.",
)

# Vite's default dev server port. Update/extend this list once the
# frontend has a real deployed URL.
_ALLOWED_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(search.router)