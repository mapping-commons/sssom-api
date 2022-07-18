from fastapi import FastAPI, HTTPException
from oaklib.implementations.ols.ols_implementation import OlsImplementation

app = FastAPI()


@app.get("/mappings/{curie_id}")
async def mapping_by_curie(curie_id: str):
    #DIGIT = 'UBERON:0002544'
    response = {}
    mappings = []
    oi = OlsImplementation()

    # test if curie_id exists

    for m in oi.get_sssom_mappings_by_curie(curie_id):
      mappings.append(m.object_id)
    
    size = len(mappings)

    if size > 0:
      response["size"] = size
      response["subject_id"] = curie_id
      response["mappings"] = mappings
    else:
      raise HTTPException(status_code=404, detail=f'No mapping found for {curie_id} ')   

    return response