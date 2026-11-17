from app.services.aws_client import get_client
from app.models.schemas import S3Bucket, S3Object


def list_buckets() -> list[S3Bucket]:
    s3 = get_client("s3")
    resp = s3.list_buckets()
    return [
        S3Bucket(
            name=b["Name"],
            creation_date=b["CreationDate"].isoformat() if b.get("CreationDate") else None,
        )
        for b in resp.get("Buckets", [])
    ]


def list_objects(bucket: str, prefix: str = "", max_keys: int = 100) -> list[S3Object]:
    s3 = get_client("s3")
    resp = s3.list_objects_v2(Bucket=bucket, Prefix=prefix, MaxKeys=max_keys)
    return [
        S3Object(
            key=obj["Key"],
            size=obj["Size"],
            last_modified=obj["LastModified"].isoformat(),
            storage_class=obj.get("StorageClass", "STANDARD"),
        )
        for obj in resp.get("Contents", [])
    ]
