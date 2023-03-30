
from typing import Iterable, TypeVar, Union, List
import itertools
import math
from toolz.recipes import countby
from toolz.itertoolz import count
import curies

from fastapi import Request

from .models import Page, PaginationInfo, FacetInfo

OBO_CURIE_CONVERTER = curies.get_obo_converter()

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
    iter_data, iter_total, iter_facets = itertools.tee(iterable, 3)
    total_items = count(iter_total)
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
        facets=_create_facets(iter_facets)
    )

def _create_facets(data: Iterable[T]) -> FacetInfo:
    iter_mj, iter_pred = itertools.tee(data)
    
    return FacetInfo(
        mapping_justification=countby(lambda d: d["mapping_justification"], iter_mj),
        predicate_id=countby(lambda d: d["predicate_id"], iter_pred),
    )

def parser_filter(datamodel: T, filter: Union[List[str], None] = None) -> Union[List[dict], None]:
  filter_pars = []

  if filter is None:
    return filter_pars

  for f in filter:
    fil = f.split("|")
    if len(fil) > 3:
      return None
    
    field, operator, value = fil
    if not hasattr(datamodel, field):
      return None
    
    if field == 'confidence':
      value = dec2sci(value)
    if field == 'subject_id' or field == 'object_id':
       value = OBO_CURIE_CONVERTER.expand(value)
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