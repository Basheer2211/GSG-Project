
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
import app.infrastructure.persistence.models

from app.core.exceptions import PermissionDeniedError
from app.presentation.routers.auth_router import router as auth_router


app = FastAPI(title="Simera API")

app.include_router(
    auth_router,
    prefix="/api/v1"
)


@app.exception_handler(PermissionDeniedError)
def permission_denied_handler(
    request: Request,
    exc: PermissionDeniedError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"detail": str(exc)}
    )
