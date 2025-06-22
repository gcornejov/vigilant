from abc import ABC, abstractmethod
from pathlib import Path


class Storage(ABC):
    @abstractmethod
    def save_image(self, data: bytes, path: str) -> None: ...


class LocalStorage(Storage):
    def save_image(self, data: bytes, path: str) -> None:
        Path(path).write_bytes(data)
