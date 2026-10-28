
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.infrastructure.persistence.db.session import get_db
from app.domain.interfaces.user_repository import IUserRepository
from app.infrastructure.persistence.repositories.user_repository import UserRepository
from app.application.services.auth_service import AuthService


def get_user_repository(
    db: Annotated[Session, Depends(get_db)]
) -> IUserRepository:
    return UserRepository(db)


def get_auth_service(
    user_repo: Annotated[
        IUserRepository,
        Depends(get_user_repository)
    ]
) -> AuthService:
    return AuthService(user_repo)
