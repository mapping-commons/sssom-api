from fastapi import FastAPI

from .routers import mappings, mapping_sets


def create_app():
    app = FastAPI()

    app.include_router(mappings.router)
    app.include_router(mapping_sets.router)
    return app


app = create_app()


