from functools import lru_cache

from pydantic import BaseSettings

from .datamodels.sparql_implementation import SparqlImpl


class Settings(BaseSettings):
    config_file: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()


@lru_cache
def get_sparql_implementation() -> SparqlImpl:
    settings = get_settings()
    return SparqlImpl(settings.config_file)