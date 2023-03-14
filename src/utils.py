
from typing import Iterable, TypeVar, Union, List
import itertools
import functools
import math

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
    iter_data, iter_total = itertools.tee(iterable)
    total_items = functools.reduce(lambda prev, curr: prev + 1, iter_total, 0)
    total_pages = math.ceil(total_items / limit)
    for idx, item in enumerate(iter_data):
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
            page_number=page, 
            total_items=total_items,
            total_pages=total_pages
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
    
    if field == 'confidence':
      value = dec2sci(value)
    filter_pars.append({"field": field, "operator": operator, "value": value})

  return filter_pars

def parse_fields_type(multivalued_fields: List, slots: List):  
  fields_list = set(multivalued_fields) & set(slots)
  fields_single = set(slots) - fields_list

  return fields_list, fields_single

# scientific e notation to decimal notation
def sci2dec(number: str) -> float:
  return float(number)

# decimal notation to scientific e notation
def dec2sci(number: float) -> str:
  return '{:.2E}'.format(float(number))