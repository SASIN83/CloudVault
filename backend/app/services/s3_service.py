import boto3
from botocore.exceptions import ClientError
from app.config import settings
from urllib.parse import quote

_client = None


def get_client():
    global _client
    if _client is None:
        if not settings.AWS_ACCESS_KEY_ID:
            raise RuntimeError("AWS S3 is not configured. Check your .env file.")
        _client = boto3.client(
            "s3",
            region_name=settings.AWS_REGION,          # real AWS region, not "auto"
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
    return _client


def upload_file(data: bytes, key: str) -> None:
    get_client().put_object(Bucket=settings.S3_BUCKET_NAME, Key=key, Body=data)


def delete_file(key: str) -> None:
    try:
        get_client().delete_object(Bucket=settings.S3_BUCKET_NAME, Key=key)
    except ClientError:
        pass  # best-effort cleanup


def copy_file(src_key: str, dst_key: str) -> None:
    get_client().copy_object(
        Bucket=settings.S3_BUCKET_NAME,
        CopySource={"Bucket": settings.S3_BUCKET_NAME, "Key": src_key},
        Key=dst_key,
    )



def presigned_download_url(key: str, filename: str, expires_in: int = 900) -> str:
    """15-min secure URL that forces the browser to save with the ORIGINAL filename."""
    safe = filename.replace('"', '').replace(';', '')
    disposition = f"attachment; filename=\"{safe}\"; filename*=UTF-8''{quote(safe)}"
    return get_client().generate_presigned_url(
        "get_object",
        Params={
            "Bucket": settings.S3_BUCKET_NAME,
            "Key": key,
            "ResponseContentDisposition": disposition,
        },
        ExpiresIn=expires_in,
    )