import tempfile
from pathlib import Path
from unittest import mock

import pytest

from vigilant.common.storage import GoogleCloudStorage, LocalStorage


def test_local_storage() -> None:
    image_path: str = tempfile.mktemp(suffix=".png")
    image_data: bytes = b"rgb_data"

    storage = LocalStorage()
    saved_path: str = storage.save_image(image_data, image_path)

    image: bytes = Path(image_path).read_bytes()

    assert (
        image_path == saved_path and Path(image_path).exists() and image == image_data
    )


class TestGoogleCloudStorage:
    @mock.patch("vigilant.common.storage.storage")
    def test_gcs_storage(
        self, gcs_storage: mock.MagicMock, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        image_path: str = tempfile.mktemp(suffix=".png")
        image_data: bytes = b"rgb_data"

        mock_bucket = mock.MagicMock()
        mock_bucket.blob.return_value.upload_from_string = lambda *args, **kwargs: Path(
            image_path
        ).write_bytes(image_data)
        mock_gcs_client = gcs_storage.Client.return_value
        mock_gcs_client.bucket.return_value = mock_bucket

        monkeypatch.setattr(
            "vigilant.common.storage.GoogleCloudStorage._build_object_uri",
            lambda *_: image_path,
        )

        storage = GoogleCloudStorage()
        saved_path: str = storage.save_image(image_data, image_path)

        image: bytes = Path(image_path).read_bytes()

        assert (
            image_path == saved_path
            and Path(image_path).exists()
            and image == image_data
        )

    def test_build_object_uri(_, monkeypatch: pytest.MonkeyPatch) -> None:
        bucket_name: str = "app_bucket"
        file_path: str = "path/path/image.png"

        monkeypatch.setenv("BUCKET_NAME", bucket_name)

        object_uri: str = GoogleCloudStorage._build_object_uri(file_path)

        assert f"{bucket_name}/{file_path}" in object_uri
