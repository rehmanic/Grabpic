"""
Main entry point for the Grabpic FastAPI application. 
Configures the app, database lifespan, routers, and exception handlers.
"""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import get_settings
from app.database import engine
from app.models import Base
from app.routers import auth, health, images, ingest


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Manages the startup and shutdown lifecycle of the FastAPI application. Creates database tables on startup."""
    Base.metadata.create_all(bind=engine)
    yield


def create_app() -> FastAPI:
    """Creates and configures the FastAPI application instance. Registers routers, exception handlers, and metadata."""
    settings = get_settings()
    app = FastAPI(title=settings.api_title, version=settings.api_version, lifespan=lifespan)

    @app.exception_handler(RequestValidationError)
    async def _validation(_request: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={"error": {"code": "VALIDATION_ERROR", "message": exc.errors()}},
        )

    @app.exception_handler(StarletteHTTPException)
    async def _http(_request: Request, exc: StarletteHTTPException) -> JSONResponse:
        detail = exc.detail
        if isinstance(detail, dict) and "error" in detail:
            return JSONResponse(status_code=exc.status_code, content=detail)
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": "HTTP_ERROR", "message": str(detail)}},
        )

    app.include_router(health.router)
    app.include_router(ingest.router)
    app.include_router(auth.router)
    app.include_router(images.router)

    @app.get("/")
    def root() -> dict[str, str]:
        return {"service": "grabpic", "docs": "/docs", "openapi": "/openapi.json"}

    return app


app = create_app()
