
from fastapi import APIRouter, HTTPException

from backend.app.services.analytics import (
    get_summary,
    get_event_trends,
    get_developer_activity,
    get_source_activity,
)

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


@router.get("/trends/hourly", tags=["Analytics"])
def hourly_trends():
    """Return event counts grouped by hour in UTC."""
    try:
        return get_event_trends()
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Hourly trend data is temporarily unavailable.",
        )


@router.get("/developers/activity", tags=["Analytics"])
def developer_activity():
    """Return event activity grouped by developer, team, and source."""
    try:
        return get_developer_activity()
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Developer activity data is temporarily unavailable.",
        )


@router.get("/sources/activity", tags=["Analytics"])
def source_activity():
    """Return activity statistics grouped by event source."""
    try:
        return get_source_activity()
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Source activity data is temporarily unavailable.",
        )
