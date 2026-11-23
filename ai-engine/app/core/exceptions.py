import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


logger = logging.getLogger("cute3d")


class Cute3DException(Exception):
    """Base exception for Cute3D AI Engine."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str = "INTERNAL_ERROR",
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code

        super().__init__(message)


class ModelNotLoadedException(Cute3DException):
    def __init__(self):
        super().__init__(
            message="Image generation model is not loaded.",
            status_code=503,
            error_code="MODEL_NOT_LOADED",
        )


class GenerationException(Cute3DException):
    def __init__(self, message="Image generation failed."):
        super().__init__(
            message=message,
            status_code=500,
            error_code="GENERATION_FAILED",
        )


class TrainingException(Cute3DException):
    def __init__(self, message="Model training failed."):
        super().__init__(
            message=message,
            status_code=500,
            error_code="TRAINING_FAILED",
        )


def register_exception_handlers(app: FastAPI) -> None:

    @app.exception_handler(Cute3DException)
    async def cute3d_exception_handler(
        request: Request,
        exc: Cute3DException,
    ):
        logger.error(
            "%s | %s",
            exc.error_code,
            exc.message,
        )

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "code": exc.error_code,
                    "message": exc.message,
                },
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ):
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Request validation failed.",
                    "details": exc.errors(),
                },
            },
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request,
        exc: StarletteHTTPException,
    ):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "code": "HTTP_ERROR",
                    "message": str(exc.detail),
                },
            },
            headers=exc.headers,
        )

    @app.exception_handler(Exception)
    async def unexpected_exception_handler(
        request: Request,
        exc: Exception,
    ):
        logger.exception("Unexpected application error")

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected server error occurred.",
                },
            },
        )
