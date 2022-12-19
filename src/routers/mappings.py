from typing import Iterator, List, Union

from fastapi import APIRouter, Depends, HTTPException, Query

from ..database.sparql_implementation import (
  SparqlImpl, 
  get_mappings_field,
  get_mappings_query,
  get_mapping_by_id )

from ..models import PaginationParams, Mapping
from ..utils import paginate, parser_filter
from ..settings import get_sparql_implementation

router = APIRouter(prefix="/mappings", tags=["mappings"])

@router.get("/", summary="Get all mappings")
def mappings(
  sparqlImpl: SparqlImpl = Depends(get_sparql_implementation), 
  pagination: PaginationParams = Depends(),
  filter: Union[List[str], None] = Query(default=None),
):
  filter_parsed = parser_filter(Mapping, filter)
  if filter_parsed is None:
    raise HTTPException(status_code=302, detail=f'Not valid filter')
  else:
    results = get_mappings_query(sparqlImpl, filter_parsed)
    return paginate(results, **pagination.dict())

@router.get("/{id}", summary="Get mapping by id")
def mapping_by_id(
  id: str,
  sparqlImpl: SparqlImpl = Depends(get_sparql_implementation)
):
  return get_mapping_by_id(sparqlImpl, id)

@router.get("/{field}/{value:path}", summary="Get mappings by any field available in Mapping datamodel")
def mappings_by_field(
  field: str,
  value: str,
  sparqlImpl: SparqlImpl = Depends(get_sparql_implementation),
  pagination: PaginationParams = Depends()
):
  if not hasattr(Mapping, field):
    raise HTTPException(status_code=302, detail=f'Not valid field {field} ')
  else: 
    results = get_mappings_field(sparqlImpl, field, value)
    return paginate(results, **pagination.dict())

