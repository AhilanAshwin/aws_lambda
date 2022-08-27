from functools import lru_cache
from pydantic import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Whats App Blaster API"
    ENVIRONMENT: str = "dev"
    SQS_URL: str = "awslambda-fastapi-dev-sqs"

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'


@lru_cache
def get_settings():
    return Settings()
