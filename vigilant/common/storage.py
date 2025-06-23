from abc import ABC, abstractmethod
from pathlib import Path
from typing import Final

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
