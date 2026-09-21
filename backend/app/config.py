from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    database_url: str = "sqlite:///./sangam.db"
    upload_dir: str = "./uploads"
    cors_origins: str = "http://localhost:5180,http://127.0.0.1:5180"
    data_mode: str = "prototype"
    app_name: str = "SANGAM"
    app_version: str = "1.0.0-prototype"

    class Config:
        env_file = ".env"
        extra = "ignore"

    @property
    def origins(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
