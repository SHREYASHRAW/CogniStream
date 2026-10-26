
from fastapi import FastAPI

from backend.app.api.analytics import router as analytics_router

app = FastAPI(
    title="CogniStream API",
    description="API for developer workflow and context-switching analytics.",
    version="0.1.0",
)


@app.get("/", tags=["General"])
def root():
    """Return basic API information."""
    return {
        "name": "CogniStream API",
        "status": "running",
        "version": "0.1.0",
    }


@app.get("/health", tags=["General"])
def health_check():
    """Check whether the API is responding."""
    return {"status": "healthy"}


app.include_router(analytics_router, prefix="/api/v1")
