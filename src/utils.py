
from typing import Iterable, TypeVar, Union, List

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

def parser_filter(datamodel: T, filter: Union[List[str], None] = None) -> Union[List[dict], None]:
  filter_pars = []

  if filter is None:
    return filter_pars

  for f in filter:
    fil = f.split(":")
    if len(fil) > 3:
      return None
    
    field, operator, value = fil
    if not hasattr(datamodel, field):
      return None

    filter_pars.append({"field": field, "operator": operator, "value": value})

  return filter_pars
