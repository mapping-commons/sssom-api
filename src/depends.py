from fastapi import HTTPException

async def is_valid(curie: str) -> bool:
  if ":" not in curie:
    raise HTTPException(status_code=404, detail=f'Not valid {curie} ')
  return True