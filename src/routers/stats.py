from ..database.sparql_implementation import (
  SparqlImpl,
  get_stats)

from fastapi import APIRouter, Depends

from ..settings import get_sparql_implementation

router = APIRouter(prefix="/stats", tags=["stats"])

@router.get("/", summary="Get general statistics on the database")
def stats(
  sparqlImp: SparqlImpl = Depends(get_sparql_implementation),
):
  results = get_stats(sparqlImp)
  return results