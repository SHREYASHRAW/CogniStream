
from fastapi import APIRouter, HTTPException

from backend.app.services.analytics import get_summary

router = APIRouter()


@router.get("/summary", tags=["Analytics"])
def summary():
    """Return high-level event and developer statistics."""
    try:
        return get_summary()
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Analytics data is temporarily unavailable.",
        )
