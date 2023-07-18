from typing import Generic, List, TypeVar, Union

from fastapi import Query, Request
from pydantic import BaseModel
from pydantic.generics import GenericModel

T = TypeVar("T")


class PaginationParams(BaseModel):
    request: Request
    limit: int = 20
    page: int = Query(default=1, ge=1)

    class Config:
        arbitrary_types_allowed = True


class PaginationInfo(BaseModel):
    previous: Union[str, None] = None
    next: Union[str, None] = None
    page_number: int
    total_items: int
    total_pages: int


class ConfidenceInfo(BaseModel):
    min: float = 0.0
    max: float = 1.0


class FacetInfo(BaseModel):
    mapping_justification: dict
    predicate_id: dict
    confidence: ConfidenceInfo


class Page(GenericModel, Generic[T]):
    data: List[T]
    pagination: PaginationInfo
    facets: FacetInfo


class SearchEntity(BaseModel):
    curies: List[str]
    mapping_justification: Union[List[str], None] = None
    predicate_id: Union[List[str], None] = None