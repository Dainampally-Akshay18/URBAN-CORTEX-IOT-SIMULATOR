from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    BIN_COUNT: int = Field(default=100, ge=1, le=10000)
    UPDATE_INTERVAL: float = Field(default=60.0, ge=1.0)
    BACKEND_URL: str = "http://localhost:8000"
    CITY_NAME: str = "Hyderabad"
    MAX_CAPACITY: float = Field(default=100.0, ge=1.0)
    INITIAL_FILL_MIN: float = Field(default=0.0, ge=0.0)
    INITIAL_FILL_MAX: float = Field(default=30.0, le=100.0)
    LAT_MIN: float = 17.30
    LAT_MAX: float = 17.45
    LON_MIN: float = 78.40
    LON_MAX: float = 78.55
    LOG_LEVEL: str = "INFO"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
