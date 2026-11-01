from abc import ABC, abstractmethod


class IFileStorage(ABC):

    @abstractmethod
    def save(self, content: bytes, extension: str) -> str:
        pass