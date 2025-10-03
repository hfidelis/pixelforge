import boto3

from botocore.client import Config
from core.settings import get_settings

settings = get_settings()

storage_client = boto3.client(
    "s3",
    endpoint_url=settings.storage_endpoint,
    aws_access_key_id=settings.storage_access_key,
    aws_secret_access_key=settings.storage_secret_key,
    region_name=settings.storage_region,
    config=Config(signature_version="s3v4"),
)


def create_bucket_if_not_exists(bucket_name: str):
    existing_buckets = storage_client.list_buckets()

    if not any(bucket['Name'] == bucket_name for bucket in existing_buckets.get('Buckets', [])):
        storage_client.create_bucket(Bucket=bucket_name)

