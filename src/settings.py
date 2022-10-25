from functools import lru_cache

from pydantic import BaseSettings, Field

from .database.sparql_implementation import SparqlImpl, OntologyResource


class Settings(BaseSettings):
    sparql_endpoint: str = Field(..., env='SPARQL_ENDPOINT')    


@lru_cache
def get_settings() -> Settings:
    return Settings()


@lru_cache
def get_sparql_implementation() -> SparqlImpl:
    settings = get_settings()
    print(settings)
    return SparqlImpl(OntologyResource(url=settings.sparql_endpoint))