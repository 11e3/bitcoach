from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    app_name: str = "bitcoach"
    environment: str = "development"
    debug: bool = True

    # Database
    database_url: str = "sqlite+aiosqlite:///data/bitcoach.db"

    # CORS
    cors_origins: str = "http://localhost:5173"

    # Anthropic
    anthropic_api_key: str = ""

    # Upbit
    upbit_api_base_url: str = "https://api.upbit.com/v1"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
