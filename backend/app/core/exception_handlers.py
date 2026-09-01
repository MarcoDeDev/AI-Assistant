import logging

from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse

from app.llm.exceptions import (
    LLMAuthenticationError,
    LLMConnectionError,
    LLMRateLimitError,
    LLMUnknownError,
)

from app.services.exceptions import ConversationNotFoundError

from app.schemas.error import ErrorResponse


logger = logging.getLogger(__name__)


def create_error_response(
    status_code: int,
    code: str,
    message: str,
) -> JSONResponse:

    response = ErrorResponse(
        error={
            "code": code,
            "message": message,
        },
    )

    return JSONResponse(
        status_code=status_code,
        content=response.model_dump(),
    )


def register_exception_handlers(
    app: FastAPI,
) -> None:

    @app.exception_handler(
        ConversationNotFoundError
    )
    async def conversation_not_found_handler(
        request: Request,
        exc: ConversationNotFoundError,
    ) -> JSONResponse:

        logger.warning(
            "Conversation not found on %s %s",
            request.method,
            request.url.path,
        )

        return create_error_response(
            status_code=404,
            code="CONVERSATION_NOT_FOUND",
            message="The requested conversation was not found.",
        )
    

    @app.exception_handler(
        LLMAuthenticationError
    )
    async def llm_authentication_handler(
        request: Request,
        exc: LLMAuthenticationError,
    ) -> JSONResponse:

        logger.error(
            "LLM authentication error on %s %s",
            request.method,
            request.url.path,
        )

        return create_error_response(
            status_code=401,
            code="LLM_AUTHENTICATION",
            message="The AI service authentication failed.",
        )

    @app.exception_handler(
        LLMRateLimitError
    )
    async def llm_rate_limit_handler(
        request: Request,
        exc: LLMRateLimitError,
    ) -> JSONResponse:

        logger.error(
            "LLM rate limit error on %s %s",
            request.method,
            request.url.path,
        )

        return create_error_response(
            status_code=429,
            code="LLM_RATE_LIMIT",
            message="The AI service rate limit or quota was exceeded.",
        )

    @app.exception_handler(
        LLMConnectionError
    )
    async def llm_connection_handler(
        request: Request,
        exc: LLMConnectionError,
    ) -> JSONResponse:

        logger.error(
            "LLM connection error on %s %s",
            request.method,
            request.url.path,
        )

        return create_error_response(
            status_code=503,
            code="LLM_CONNECTION",
            message="The AI service is currently unavailable.",
        )

    @app.exception_handler(
        LLMUnknownError
    )
    async def llm_unknown_handler(
        request: Request,
        exc: LLMUnknownError,
    ) -> JSONResponse:

        logger.error(
            "Unknown LLM error on %s %s",
            request.method,
            request.url.path,
        )

        return create_error_response(
            status_code=500,
            code="LLM_UNKNOWN",
            message="An unexpected AI service error occurred.",
        )