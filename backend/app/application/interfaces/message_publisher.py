from abc import ABC, abstractmethod


class IMessagePublisher(ABC):
    """Hands an accepted source file (a job) to the background workers."""

    @abstractmethod
    def publish_file_job(self, file_id: int) -> None:
        pass
