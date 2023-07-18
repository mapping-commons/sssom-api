import itertools
import json
import math
from typing import Iterable, List, Tuple, TypeVar, Union

from curies import Converter
from fastapi import Request
from fastapi.datastructures import QueryParams
from toolz.itertoolz import count
from toolz.recipes import countby

from .models import ConfidenceInfo, FacetInfo, Page, PaginationInfo

T = TypeVar("T")

with open("../resources/obo.context.jsonld") as f:
    OBO_CONTEXT = json.load(f)
CURIE_OBO_CONVERTER = Converter.from_prefix_map(OBO_CONTEXT["@context"])

def parser_filter(
    datamodel: object,
     query_params: QueryParams
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