from fastapi import FastAPI

from .routers import mappings


def create_app():
    app = FastAPI()

    app.include_router(mappings.router)
    return app


app = create_app()


