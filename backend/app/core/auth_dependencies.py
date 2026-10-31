
from typing import Annotated

import jwt

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.security import decode_access_token


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login"
)


def get_current_user_id(
    token: Annotated[str, Depends(oauth2_scheme)]
) -> int:

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired access token",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        payload = decode_access_token(token)

        if payload.get("type") != "access":
            raise credentials_exception

        user_id = payload.get("sub")

        if not isinstance(user_id, str):
            raise credentials_exception

        parsed_user_id = int(user_id)

        if parsed_user_id <= 0:
            raise credentials_exception

        return parsed_user_id

    except (jwt.InvalidTokenError, ValueError, TypeError):
        raise credentials_exception
