
from fastapi import FastAPI
import app.infrastructure.persistence.models
from app.presentation.routers.cv_router import router as cv_router

from app.presentation.routers.auth_router import router as auth_router


app = FastAPI(title="Simera API")

app.include_router(
    auth_router,
    prefix="/api/v1"
)
app.include_router(
    cv_router,
    prefix="/api/v1"
)