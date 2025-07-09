from minio import Minio

from app.core import settings
from app.core.utils.logger import logger


def init_minio_client() -> Minio:
    logger.info(f"Initializing MinIO client with endpoint: {settings.MINIO_UPLOAD_ENDPOINT}")
    
    try:
        return Minio(
            endpoint=settings.MINIO_UPLOAD_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )
    except Exception as e:
        logger.error(f"Error initializing MinIO client: {e}")
        raise e


minio_client = init_minio_client()
