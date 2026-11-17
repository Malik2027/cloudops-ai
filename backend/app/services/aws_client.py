import boto3
from app.config import settings


def get_client(service: str):
    return boto3.client(service, region_name=settings.AWS_REGION)


def get_resource(service: str):
    return boto3.resource(service, region_name=settings.AWS_REGION)
