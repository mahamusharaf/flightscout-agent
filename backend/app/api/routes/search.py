from fastapi import APIRouter, HTTPException
from app.models.schemas import SearchRequest, SearchResponse
from app.agent.agent import agent_executor

router = APIRouter()

@router.post("/search", response_model=SearchResponse)
def search_flights(request: SearchRequest):
    """
    Main agent-driven flight search & scoring endpoint.
    Processes natural language constraints, queries Duffel, calculates multi-criteria scores, and explains trade-offs.
    """
    try:
        response = agent_executor.execute_search(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent search execution failed: {str(e)}")
