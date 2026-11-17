from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import health, ec2, s3, cloudwatch, ai

app = FastAPI(
    title="CloudOps AI",
    description="AI-powered AWS cloud operations API for HRMS infrastructure",
    version="1.0.0",
    docs_url="/docs" if settings.ENV != "prod" else None,
    redoc_url="/redoc" if settings.ENV != "prod" else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(ec2.router, prefix="/api/v1")
app.include_router(s3.router, prefix="/api/v1")
app.include_router(cloudwatch.router, prefix="/api/v1")
app.include_router(ai.router, prefix="/api/v1")
