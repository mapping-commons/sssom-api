from functools import lru_cache

from pydantic import BaseSettings

from .database.sparql_implementation import SparqlImpl, OntologyResource


class Settings(BaseSettings):
    sparql_endpoint: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()


@lru_cache
def get_sparql_implementation() -> SparqlImpl:
    settings = get_settings()
    return SparqlImpl(OntologyResource(url=settings.sparql_endpoint))