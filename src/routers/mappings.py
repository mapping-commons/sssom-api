from typing import List

from fastapi import APIRouter, Depends

from ..models import PaginationParams, Mapping
from ..depends import is_valid
from ..utils import paginate
from oaklib.implementations.ols.ols_implementation import OlsImplementation

router = APIRouter(prefix="/mappings", tags=["mappings"])

@router.get("/{curie_id}", response_model=List[Mapping], summary="Get mappings by CURIE")
def mappings_by_curie(
  curie_id: str = Depends(is_valid), 
  pagination: PaginationParams = Depends()
):
  response = {}
  mappings = []
  oi = OlsImplementation()

  for m in oi.get_sssom_mappings_by_curie(curie_id):
    mapping = {}
    mapping["predicate_id"] = m.predicate_id
    mapping["object_id"] = m.object_id
    mapping["object_label"] = m.object_label
    mappings.append(mapping)
  
  
  response["subject_id"] = curie_id
  response["mappings"] = mappings

  return paginate(response, **pagination.dict())