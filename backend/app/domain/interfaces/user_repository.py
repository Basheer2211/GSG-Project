
from abc import ABC, abstractmethod

from app.domain.entities.user import User


class IUserRepository(ABC):

    @abstractmethod
    def create(self, user: User) -> User:
        pass

    @abstractmethod
    def get_by_email(self, email: str) -> User | None:
        pass
