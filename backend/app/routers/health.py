from fastapi import APIRouter
from app.models.schemas import HealthResponse
from app.config import settings

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["Health"])
def health():
    return HealthResponse(status="healthy", env=settings.ENV, region=settings.AWS_REGION)
