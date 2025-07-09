import os
from uuid import uuid4

from minio import Minio
from minio.error import S3Error

from app.core import settings
from app.core.utils.logger import logger
from app.core.minio_client import minio_client


class FileService:
    def __init__(self, client: Minio):
        self.client = client
        self.bucket_name = settings.MINIO_BUCKET_NAME
        self.public_endpoint = settings.MINIO_PUBLIC_ENDPOINT

    def upload(self, file, folder: str = "uploads") -> str:
        ext = os.path.splitext(file.name)[-1]
        unique_name = f"{uuid4().hex}{ext}"
        object_name = f"{folder}/{unique_name}"

        if not self.client.bucket_exists(self.bucket_name):
            self.client.make_bucket(self.bucket_name)

        if file.size > settings.MINIO_MAX_SIZE:
            raise ValueError("File size exceeds the maximum allowed size")

        self.client.put_object(
            bucket_name=self.bucket_name,
            object_name=object_name,
            data=file.file,
            length=file.size,
            content_type=file.content_type,
        )
        
        return f"{self.get_base_endpoint()}/{object_name}"

    def delete(self, url: str):
        object_name = self.get_object_name(url)
        
        try:
            self.client.remove_object(self.bucket_name, object_name)
            return True
        except S3Error as e:
            logger.error(f"Error deleting file from MinIO: {e}")
            return False
        
    def get_base_endpoint(self) -> str:
        return f"{self.public_endpoint}/{self.bucket_name}"
    
    def get_object_name(self, url: str) -> str:
        base_path = self.get_base_endpoint()
        if not base_path in url:
            raise ValueError("Invalid URL")

        prefixes = [
            'https://',
            'http://',
            base_path,
        ]

        for prefix in prefixes:
            url = url.replace(prefix, "")

        object_name = url.strip("/")

        return object_name


file_service = FileService(minio_client)
