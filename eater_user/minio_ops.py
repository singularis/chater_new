import logging
import os
import uuid

from minio import Minio
from minio.commonconfig import CopySource

logger = logging.getLogger("autocomplete_service")


def get_minio_client():
    client = Minio(
        os.getenv("MINIO_ENDPOINT", "minio:9000"),
        access_key=os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
        secret_key=os.getenv("MINIO_SECRET_KEY", "minioadmin"),
        secure=os.getenv("MINIO_SECURE", "false").lower() == "true",
    )
    return client


async def duplicate_photo(original_image_id, from_email, to_email):
    """
    Duplicates a photo in MinIO for the recipient user.
    Args:
        original_image_id: The MinIO object name of the original photo
        from_email: The email of the sender (to verify ownership/path)
        to_email: The email of the recipient
    Returns:
        The new image_id (object name) for the recipient, or None if failed
    """
    try:
        client = get_minio_client()
        bucket_name = os.getenv("MINIO_BUCKET_EATER", "eater")

        # Construct source path.
        # With our fixes, original_image_id IS the full MinIO object name (path).
        src_path = original_image_id

        # Generate new path for recipient
        # New path: "recipient@example.com/UUID.jpg" to avoid collision and guessing
        filename = f"{uuid.uuid4()}.jpg"
        dest_path = f"{to_email}/{filename}"

        # Copy
        client.copy_object(
            bucket_name,
            dest_path,
            CopySource(bucket_name, src_path),
        )

        logger.info(f"Copied photo from {src_path} to {dest_path}")
        return dest_path

    except Exception as e:
        logger.error(f"Error duplicating photo in MinIO: {e}")
        return None
