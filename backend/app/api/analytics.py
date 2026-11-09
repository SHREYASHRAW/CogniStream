
from fastapi import APIRouter, HTTPException

from backend.app.services.analytics import (
    get_summary,
    get_event_trends,
    get_developer_activity,
    get_source_activity,
    get_context_switches,
    get_transition_summary,
    get_developer_transition_summary,
)

router = APIRouter()


@router.get("/summary", tags=["Analytics"])
def analytics_summary():
    """Return overall analytics summary."""
    try:
        return get_summary()
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Analytics summary data is temporarily unavailable.",
        )


@router.get("/trends/hourly", tags=["Analytics"])
def hourly_trends():
    """Return hourly event trends."""
    try:
        return get_event_trends()
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Hourly trend data is temporarily unavailable.",
        )


@router.get("/developers/activity", tags=["Analytics"])
def developer_activity():
    """Return event activity grouped by developer and team."""
    try:
        return get_developer_activity()
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Developer activity data is temporarily unavailable.",
        )


@router.get("/sources/activity", tags=["Analytics"])
def source_activity():
    """Return event activity grouped by source."""
    try:
        return get_source_activity()
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Source activity data is temporarily unavailable.",
        )


@router.get("/context-switches", tags=["Analytics"])
def context_switches():
    """Return potential context switches between consecutive developer events."""
    try:
        return get_context_switches()
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Context-switch data is temporarily unavailable.",
        )


@router.get("/transitions/summary", tags=["Analytics"])
def transition_summary():
    """Return aggregated source-transition statistics by team and source pair."""
    try:
        return get_transition_summary()
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Transition summary data is temporarily unavailable.",
        )


@router.get("/developers/transitions/summary", tags=["Analytics"])
def developer_transition_summary():
    """Return source-transition statistics grouped by developer and team."""
    try:
        return get_developer_transition_summary()
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Developer transition summary data is temporarily unavailable.",
        )
