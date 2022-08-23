from typing import Iterable, TypeVar, Union

from fastapi import Request

from .models import Page, PaginationInfo


def _replace_page_param(request: Request, new_page: Union[int, None]) -> Union[str, None]:
    if new_page is None:
        return None
    return str(request.url.include_query_params(page=new_page))


T = TypeVar("T")


def paginate(iterable: Iterable[T], page: int, limit: int, request: Request) -> Page[T]:
    start = (page - 1) * limit
    stop = page * limit
    prev_page = None
    next_page = None
    data = []
    for idx, item in enumerate(iterable):
        if idx == start - 1:
            prev_page = page - 1
        if idx >= start and idx < stop:
            data.append(item)
        if idx >= stop:
            next_page = page + 1
            break
    return Page(
        data=data,
        pagination=PaginationInfo(
            previous=_replace_page_param(request, prev_page),
            next=_replace_page_param(request, next_page),
        ),
    )