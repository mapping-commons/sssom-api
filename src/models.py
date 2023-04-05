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


class Page(GenericModel, Generic[T]):
    data: List[T]
    pagination: PaginationInfo


class SearchEntity(BaseModel):
    curies: List[str]
