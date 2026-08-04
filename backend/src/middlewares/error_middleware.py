from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from src.services.evolution_service import EvolutionError
from src.utils.logger import logger


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(status_code=422, content={"detail": exc.errors()})

    @app.exception_handler(EvolutionError)
    async def evolution_exception_handler(request: Request, exc: EvolutionError):
        logger.error(f"Erro Evolution API em {request.url.path}: {exc}")
        return JSONResponse(status_code=502, content={"detail": str(exc)})

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.exception(f"Erro não tratado em {request.url.path}: {exc}")
        return JSONResponse(status_code=500, content={"detail": "Erro interno do servidor"})
