from fastapi import APIRouter, Depends

from backend.src.repository import solr_stats

router = APIRouter(prefix="/stats", tags=["stats"])

@router.get(path="/", summary="Get general statistics on the database")
def stats():
    return solr_stats()
