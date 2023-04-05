from typing import List, Union

from fastapi import APIRouter, Depends, HTTPException, Query
from sssom_schema import Mapping

from ..database.sparql_implementation import (
    SparqlImpl,
    get_ui_mapping_by_id,
    get_mapping_by_id,
    get_mappings_field,
    get_mappings_query,
)
from ..models import PaginationParams
from ..settings import get_sparql_implementation
from ..utils import paginate, parser_filter

router = APIRouter(prefix="/mappings", tags=["mappings"])


@router.get(path="/", summary="Get all mappings")
def mappings(
    sparqlImpl: SparqlImpl = Depends(get_sparql_implementation),
    pagination: PaginationParams = Depends(),
    filter: Union[List[str], None] = Query(default=None),
):
    filter_parsed = parser_filter(Mapping, filter)
    if filter_parsed is None:
        raise HTTPException(status_code=302, detail="Not valid filter")
    else:
        results = get_mappings_query(sparqlImpl, filter_parsed)
        return paginate(results, **pagination.dict())


@router.get(path="/{id}", summary="Get mapping by id")
def mapping_by_id(id: str, sparqlImpl: SparqlImpl = Depends(get_sparql_implementation)):
    return get_mapping_by_id(sparqlImpl, id)


@router.get(
    path="/{field}/{value:path}", summary="Get mappings by any field available in Mapping datamodel"
)
def mappings_by_field(
    field: str,
    value: str,
    sparqlImpl: SparqlImpl = Depends(get_sparql_implementation),
    pagination: PaginationParams = Depends(),
):
    if not hasattr(Mapping, field):
        raise HTTPException(status_code=302, detail=f"Not valid field {field}")
    else:
        results = get_mappings_field(sparqlImpl, field, value)
        return paginate(results, **pagination.dict())


router_ui = APIRouter(prefix="/mappings", tags=["mappings"])

@router_ui.get("/{id}", summary="Get mapping by id")
def mapping_by_id_ui(
    id: str,
    sparqlImpl: SparqlImpl = Depends(get_sparql_implementation)
):
    return get_ui_mapping_by_id(sparqlImpl, id)