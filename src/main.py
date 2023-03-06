from fastapi import FastAPI

from .routers import mappings, mapping_sets, entities, stats


def create_app():
    app = FastAPI()

    app.include_router(mappings.router)
    app.include_router(mapping_sets.router)
    app.include_router(entities.router)
    app.include_router(stats.router)
    return app


app = create_app()


