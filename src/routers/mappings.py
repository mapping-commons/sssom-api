from typing import Iterator, List

from fastapi import APIRouter, Depends, HTTPException

from ..database.sparql_implementation import SparqlImpl, get_mappings, get_mappings_field

from ..models import Page, PaginationParams, Mapping
from ..depends import is_valid
from ..utils import paginate
from ..settings import get_sparql_implementation

router = APIRouter(prefix="/mappings", tags=["mappings"])

# @router.get("/", summary="Get mappings")
# def mappings(
#   sparqlImpl: SparqlImpl = Depends(get_sparql_implementation), 
#   pagination: PaginationParams = Depends()
# ):
#   results = get_mappings(sparqlImpl)
#   return paginate(results, **pagination.dict())

# response_model=Page[Mapping]
@router.get("/{curie}", summary="Get mappings by CURIE")
def mappings_by_curie(
  sparqlImpl: SparqlImpl = Depends(get_sparql_implementation),
  curie: str = Depends(is_valid),
  pagination: PaginationParams = Depends()
):
  results = get_mappings(sparqlImpl, curie)
  return paginate(results, **pagination.dict())

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