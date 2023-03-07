from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import mappings, mapping_sets, entities, stats


def create_app():
    app = FastAPI()

    app.add_middleware(
      CORSMiddleware,
      allow_origins=["*"],
      allow_credentials=True,
      allow_methods=["*"],
      allow_headers=["*"]
    )

    app.include_router(mappings.router)
    app.include_router(mapping_sets.router)
    app.include_router(entities.router)
    app.include_router(stats.router)
    return app


app = create_app()


