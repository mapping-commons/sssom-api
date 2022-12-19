from ..database.sparql_implementation import (
  SparqlImpl, 
  get_mappings)

from fastapi import APIRouter, Depends

from ..models import PaginationParams
from ..utils import paginate
from ..depends import is_valid
from ..settings import get_sparql_implementation

router = APIRouter(prefix="/entities", tags=["entities"])

@router.get("/{curie}", summary="Get mappings by CURIE, both in subject_id or object_id")
def mappings_by_curie(
  sparqlImpl: SparqlImpl = Depends(get_sparql_implementation),
  curie: str = Depends(is_valid),
  pagination: PaginationParams = Depends()
):
  results = get_mappings(sparqlImpl, curie)
  return paginate(results, **pagination.dict())
