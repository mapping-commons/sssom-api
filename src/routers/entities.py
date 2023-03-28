from ..database.sparql_implementation import (
  SparqlImpl, 
  get_mappings,
  get_mappings_ui)

from fastapi import APIRouter, Depends

from ..models import PaginationParams, SearchEntity
from ..utils import paginate
from ..depends import is_valid
from ..settings import get_sparql_implementation

router = APIRouter(prefix="/entities", tags=["entities"])

@router.post("/", summary="Get mappings by CURIE, both in subject_id or object_id")
def mappings_by_curie(
  curies: SearchEntity,
  sparqlImpl: SparqlImpl = Depends(get_sparql_implementation),
  pagination: PaginationParams = Depends()
):
  results = get_mappings(sparqlImpl, curies)
  return paginate(results, **pagination.dict())

router_ui = APIRouter(prefix="/entities", tags=["entities"])
@router_ui.post("/", summary="Get mappings by CURIE, both in subject_id or object_id")
def mappings_by_curie(
  curies: SearchEntity,
  sparqlImpl: SparqlImpl = Depends(get_sparql_implementation),
  pagination: PaginationParams = Depends()
):
  results = get_mappings_ui(sparqlImpl, curies)
  return paginate(results, **pagination.dict())