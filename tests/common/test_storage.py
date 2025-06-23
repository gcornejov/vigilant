import tempfile
from pathlib import Path

from vigilant.common.storage import LocalStorage


def test_local_storage() -> None:
    image_path: str = tempfile.mktemp(suffix=".png")
    image_data: bytes = b"rgb_data"

    storage = LocalStorage()
    saved_path: str = storage.save_image(image_data, image_path)

    image: bytes = Path(image_path).read_bytes()

    assert (
        image_path == saved_path and Path(image_path).exists() and image == image_data
    )
