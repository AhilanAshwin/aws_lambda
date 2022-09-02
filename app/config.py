from functools import lru_cache
from pydantic import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Whats App Blaster API"
    STAGE: str = "local"
    SQS_URL: str = "awslambda-fastapi-dev-sqs-local"
    LOCAL_MOUNT_PATH: str = "./"

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'


@lru_cache
def get_settings():
    return Settings()
