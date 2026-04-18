"""
Router for health check and service status endpoints.
"""
from fastapi import APIRouter

from app.config import get_settings
from app.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Returns the current health status and version of the API."""
    return HealthResponse(status="ok", version=get_settings().api_version)
