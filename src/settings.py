from functools import lru_cache

from oaklib.resource import OntologyResource
from pydantic import BaseSettings, Field
from sssom.constants import SSSOMSchemaView  # type: ignore

from .database.sparql_implementation import SparqlImpl


class Settings(BaseSettings):
    sparql_endpoint: str = Field(..., env="SPARQL_ENDPOINT")


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore


@lru_cache
def get_sparql_implementation() -> SparqlImpl:
    settings = get_settings()
    schema_view = SSSOMSchemaView()
    return SparqlImpl(
        OntologyResource(url=settings.sparql_endpoint),
        schema_view=schema_view,  # type: ignore
    )
