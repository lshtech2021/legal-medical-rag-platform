import boto3

from app.core.config import settings


class StorageService:
    def __init__(self) -> None:
        self.client = boto3.client("s3", region_name=settings.aws_region)

    def put_bytes(self, key: str, payload: bytes, content_type: str) -> None:
        self.client.put_object(Bucket=settings.s3_bucket, Key=key, Body=payload, ContentType=content_type)
