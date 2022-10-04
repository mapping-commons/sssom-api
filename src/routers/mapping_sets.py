from typing import List, Union

from fastapi import APIRouter, Depends, Query, HTTPException

from ..database.sparql_implementation import SparqlImpl, get_mapping_sets

from ..models import PaginationParams, MappingSet
from ..utils import paginate, parser_filter
from ..settings import get_sparql_implementation

router = APIRouter(prefix="/mapping_sets", tags=["mapping_sets"])

@router.get("/", summary="Get all mapping sets with option to filter")
def mapping_sets(
  sparqlImpl: SparqlImpl = Depends(get_sparql_implementation),
  pagination: PaginationParams = Depends(),
  filter: Union[List[str], None] = Query(default=None),
):
  filter_parsed = parser_filter(MappingSet, filter)
  if filter_parsed is None:
    raise HTTPException(status_code=404, detail=f'Not valid filter')
  else:
    results = get_mapping_sets(sparqlImpl, filter_parsed)
    return paginate(results, **pagination.dict())