from typing import Annotated, Callable

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.infrastructure.persistence.db.session import get_db
from app.domain.entities.user import User
from app.domain.interfaces.user_repository import IUserRepository
from app.domain.permissions import Permission, has_permission
from app.infrastructure.persistence.repositories.user_repository import UserRepository
from app.application.services.auth_service import AuthService
from app.core.security import decode_access_token


bearer_scheme = HTTPBearer(auto_error=False)


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


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"}
    )


def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(bearer_scheme)
    ],
    user_repo: Annotated[
        IUserRepository,
        Depends(get_user_repository)
    ]
) -> User:
    """Return the user making the request, or respond 401."""
    if credentials is None:
        raise _unauthorized("Not authenticated")

    try:
        payload = decode_access_token(credentials.credentials)
        user_id = int(payload["sub"])
    except (jwt.InvalidTokenError, ValueError) as exc:
        raise _unauthorized("Invalid or expired token") from exc

    user = user_repo.get_by_id(user_id)

    if user is None:
        raise _unauthorized("Invalid or expired token")

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_permission(*permissions: Permission) -> Callable[..., User]:
    """Role guard: respond 403 unless the user's role has every permission.

    Usage:
        @router.get("/review/queue")
        def queue(user: Annotated[User, Depends(require_permission(Permission.REVIEW_QUEUE))]):
            ...
    """
    def dependency(user: CurrentUser) -> User:
        if not all(has_permission(user.role, p) for p in permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action"
            )
        return user

    return dependency
