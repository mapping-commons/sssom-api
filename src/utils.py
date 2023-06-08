import itertools
import json
import math
from typing import Iterable, List, Tuple, TypeVar, Union

from curies import Converter
from fastapi import Request
from toolz.itertoolz import count
from toolz.recipes import countby

from .models import ConfidenceInfo, FacetInfo, Page, PaginationInfo

T = TypeVar("T")

with open("./resources/obo.context.jsonld") as f:
    OBO_CONTEXT = json.load(f)
CURIE_OBO_CONVERTER = Converter.from_prefix_map(OBO_CONTEXT["@context"])


def _replace_page_param(request: Request, new_page: Union[int, None]) -> Union[str, None]:
    if new_page is None:
        return None
    return str(request.url.include_query_params(page=new_page))


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
            total_pages=total_pages,
        ),
        facets=_create_facets(iter_facets),
    )


def _create_facets(data: Iterable[object]) -> FacetInfo:
    iter_mj, iter_pred, iter_conf = itertools.tee(data, 3)

    list_iter_conf = list(iter_conf)
    return FacetInfo(
        mapping_justification=countby(lambda d: d["mapping_justification"], iter_mj),
        predicate_id=countby(lambda d: d["predicate_id"], iter_pred),
        confidence=ConfidenceInfo(
            min=min(
                map(
                    lambda d: d["confidence"] if d.get("confidence") else 0.0,  # type: ignore
                    list_iter_conf,
                )
            ),
            max=max(
                map(
                    lambda d: d["confidence"] if d.get("confidence") else 0.0,  # type: ignore
                    list_iter_conf,
                )
            ),
        ),
    )


def parser_filter(
    datamodel: object, filter: Union[List[str], None] = None
) -> Union[List[dict], None]:
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

        if field == "confidence":
            value = dec2sci(float(value))
        if field == "subject_id" or field == "object_id":
            value = expand_uri(value)
        if field == "predicate_id":
            value = expand_uri(value)
        filter_pars.append({"field": field, "operator": operator, "value": value})

    return filter_pars


def parse_fields_type(multivalued_fields: List[str], slots: List[str]) -> Tuple[set, set]:
    fields_list = set(multivalued_fields) & set(slots)
    fields_single = set(slots) - fields_list

    return fields_list, fields_single


# scientific e notation to decimal notation
def sci2dec(number: str) -> float:
    return float(number)


# decimal notation to scientific e notation
def dec2sci(number: float) -> str:
    return "{:.2E}".format(float(number))


def expand_uri(uri: str) -> str:
    return str(CURIE_OBO_CONVERTER.expand(uri))


def compress_uri(uri: str) -> str:
    return str(CURIE_OBO_CONVERTER.compress(uri))
