from typing import List, Union

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from ..database.sparql_implementation import (
    SparqlImpl,
    get_mapping_sets,
    get_mappings_by_mapping_set,
)
from ..models import MappingSet, PaginationParams
from ..settings import get_sparql_implementation
from ..utils import paginate, parser_filter

router = APIRouter(prefix="/mapping_sets", tags=["mapping_sets"])


@router.get("/", summary="Get all mapping sets with option to filter")
def mapping_sets(
    request: Request,
    sparqlImpl: SparqlImpl = Depends(get_sparql_implementation),
    pagination: PaginationParams = Depends(),
    filter: Union[List[str], None] = Query(default=None),
):
    filter_parsed = parser_filter(MappingSet, filter)
    if filter_parsed is None:
        raise HTTPException(status_code=404, detail="Not valid filter")
    else:
        results = get_mapping_sets(request, sparqlImpl, filter_parsed)
        return paginate(results, **pagination.dict())


@router.get("/{id}/mappings", summary="Get all mappings for a mapping set")
def mappings_by_mapping_set(
    id: str,
    sparqlImpl: SparqlImpl = Depends(get_sparql_implementation),
    pagination: PaginationParams = Depends(),
):
    results = get_mappings_by_mapping_set(sparqlImpl, id)
    return paginate(results, **pagination.dict())
