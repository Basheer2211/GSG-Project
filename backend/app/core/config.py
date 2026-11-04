
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Message queue for background processing. When unset, jobs are stored
    # with status 'uploaded' but not published.
    RABBITMQ_URL: str | None = None
    CV_JOB_QUEUE: str = "cv_processing"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()
