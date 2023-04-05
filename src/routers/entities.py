from fastapi import APIRouter, Depends

from ..database.sparql_implementation import SparqlImpl, get_mappings
from ..models import PaginationParams, SearchEntity
from ..settings import get_sparql_implementation
from ..utils import paginate

router = APIRouter(prefix="/entities", tags=["entities"])


@router.post(path="/", summary="Get mappings by CURIE, both in subject_id or object_id")
def mappings_by_curie(
    curies: SearchEntity,
    sparqlImpl: SparqlImpl = Depends(get_sparql_implementation),
    pagination: PaginationParams = Depends(),
):
    results = get_mappings(sparqlImpl, curies)
    return paginate(results, **pagination.dict())
