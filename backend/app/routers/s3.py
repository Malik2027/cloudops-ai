from fastapi import APIRouter, Depends, Query
from app.dependencies import verify_api_key
from app.models.schemas import S3Bucket, S3Object
from app.services import s3_service

router = APIRouter(prefix="/s3", tags=["S3"], dependencies=[Depends(verify_api_key)])


@router.get("/buckets", response_model=list[S3Bucket])
def list_buckets():
    return s3_service.list_buckets()


@router.get("/buckets/{bucket}/objects", response_model=list[S3Object])
def list_objects(
    bucket: str,
    prefix: str = Query("", description="Key prefix filter"),
    max_keys: int = Query(100, ge=1, le=1000),
):
    return s3_service.list_objects(bucket, prefix=prefix, max_keys=max_keys)
