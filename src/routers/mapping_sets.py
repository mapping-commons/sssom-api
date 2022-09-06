from fastapi import APIRouter, Depends

from ..database.sparql_implementation import SparqlImpl, get_mapping_sets

from ..models import PaginationParams
from ..utils import paginate
from ..settings import get_sparql_implementation

router = APIRouter(prefix="/mapping_sets", tags=["mapping_sets"])

@router.get("/", summary="Get mapping sets")
def mapping_sets_by_id(
  sparqlImpl: SparqlImpl = Depends(get_sparql_implementation),
  pagination: PaginationParams = Depends()
):
  results = get_mapping_sets(sparqlImpl)
  return paginate(results, **pagination.dict())