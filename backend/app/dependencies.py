import boto3
from fastapi import Header, HTTPException, status
from functools import lru_cache

from app.config import settings


def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != settings.API_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")


@lru_cache(maxsize=1)
def get_aws_session() -> boto3.Session:
    return boto3.Session(region_name=settings.AWS_REGION)
