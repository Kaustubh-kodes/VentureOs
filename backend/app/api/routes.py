from datetime import datetime, timezone
from fastapi import APIRouter
from app.schemas.health import HealthResponse, RootResponse

router = APIRouter()


@router.get("/", response_model=RootResponse)
async def root():
    """Root endpoint — confirms the API is running."""
    return RootResponse(message="Welcome to VentureOS API")


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint used by frontend and load balancers."""
    return HealthResponse(
        status="healthy",
        service="ventureos-api",
        version="0.9.0",
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
