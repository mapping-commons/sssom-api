from typing import List, Union

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sssom_schema import Mapping

from ..models import PaginationParams
from ..repository import get_mappings, get_mappings_by_id
from ..utils import parser_filter

router = APIRouter(prefix="/mappings", tags=["mappings"])

@router.get(path="/", summary="Get mappings")
def mappings(
    request:Request,
    min_confidence:float = None,
    max_confidence:float = None,
    pagination: PaginationParams = Depends()
):
    return get_mappings(pagination, request.query_params, min_confidence, max_confidence)

@router.get(path="/{id}", summary="Get mapping by id")
def mapping_by_id(id: str):
    return get_mappings_by_id(id)


