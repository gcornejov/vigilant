from abc import ABC, abstractmethod
from pathlib import Path
from typing import Final

from google.cloud import storage

from vigilant.common.values import Environment

DEFAULT_PATH: Final[str] = "."


class Storage(ABC):
    @abstractmethod
    def save_image(self, data: bytes, path: str) -> str: ...


class LocalStorage(Storage):
    def save_image(self, data: bytes, path: str = DEFAULT_PATH) -> str:
        """Save image in local file system

        Args:
            data (bytes): Image data
            path (str, optional): Path where to save the image. Defaults to DEFAULT_PATH.

        Returns:
            str: Path where the image was saved
        """
        image_path = Path(path)
        image_path.parents[0].mkdir(parents=True, exist_ok=True)

        image_path.write_bytes(data)
        return image_path.as_posix()


class GoogleCloudStorage(Storage):
    def __init__(self):
        storage_client = storage.Client()
        self.bucket: storage.Bucket = storage_client.bucket(Environment.BUCKET_NAME)

    def save_image(self, data: bytes, path: str = "") -> str:
        """Save image in GCS bucket

        Args:
            data (bytes): Image data
            path (str, optional): Path where to save the image. Defaults to "".

        Returns:
            str: URI of the image as GCS object
        """
        blob: storage.Blob = self.bucket.blob(path)
        blob.upload_from_string(data, content_type="image/png")

        return self._build_object_uri(path)

    @staticmethod
    def _build_object_uri(object_path: str) -> str:
        GCS_BASE_URL: Final[str] = "https://storage.cloud.google.com"

        return f"{GCS_BASE_URL}/{Environment.BUCKET_NAME}/{object_path}"
