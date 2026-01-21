import io
import os
from urllib.parse import urlparse

from minio import Minio
from minio.error import S3Error


def _parse_endpoint_and_secure(
    raw_endpoint: str | None, default_secure: bool
) -> tuple[str, bool]:
    if not raw_endpoint:
        return ("localhost:9000", default_secure)
    parsed = urlparse(raw_endpoint)
    if parsed.scheme:
        secure = parsed.scheme == "https"
        netloc = parsed.netloc or parsed.path
        return (netloc, secure)
    return (raw_endpoint, default_secure)


def get_minio_client() -> Minio:
    raw_endpoint = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    secure_env = os.getenv("MINIO_SECURE", "false").lower() == "true"
    endpoint, secure = _parse_endpoint_and_secure(raw_endpoint, secure_env)
    access_key = os.getenv("MINIO_ACCESS_KEY")
    secret_key = os.getenv("MINIO_SECRET_KEY")
    if not access_key or not secret_key:
        raise RuntimeError("MINIO_ACCESS_KEY or MINIO_SECRET_KEY not configured")
    return Minio(endpoint, access_key=access_key, secret_key=secret_key, secure=secure)


def put_bytes(
    client: Minio,
    bucket_name: str,
    object_name: str,
    data: bytes,
    *,
    content_type: str | None = None,
) -> None:
    data_stream = io.BytesIO(data)
    length = len(data)
    client.put_object(
        bucket_name,
        object_name,
        data_stream,
        length=length,
        content_type=content_type,
    )
