from fastapi.testclient import TestClient

from app.core.dependencies import get_chat_service
from app.llm.base import BaseLLM
from app.llm.exceptions import (
    LLMAuthenticationError,
    LLMConnectionError,
    LLMRateLimitError,
    LLMUnknownError,
)
from app.llm.llm_response import LLMResponse
from app.main import app
from app.services.chat_service import ChatService


class RateLimitLLM(BaseLLM):

    def generate(
        self,
        prompt: str,
    ) -> LLMResponse:

        raise LLMRateLimitError()


class AuthenticationErrorLLM(BaseLLM):

    def generate(
        self,
        prompt: str,
    ) -> LLMResponse:

        raise LLMAuthenticationError()


class ConnectionErrorLLM(BaseLLM):

    def generate(
        self,
        prompt: str,
    ) -> LLMResponse:

        raise LLMConnectionError()


class UnknownErrorLLM(BaseLLM):

    def generate(
        self,
        prompt: str,
    ) -> LLMResponse:

        raise LLMUnknownError()


def get_rate_limit_chat_service() -> ChatService:

    return ChatService(
        llm=RateLimitLLM(),
    )


def get_authentication_error_chat_service() -> ChatService:

    return ChatService(
        llm=AuthenticationErrorLLM(),
    )


def get_connection_error_chat_service() -> ChatService:

    return ChatService(
        llm=ConnectionErrorLLM(),
    )


def get_unknown_error_chat_service() -> ChatService:

    return ChatService(
        llm=UnknownErrorLLM(),
    )


def test_chat_rate_limit_error() -> None:

    app.dependency_overrides[
        get_chat_service
    ] = get_rate_limit_chat_service

    client = TestClient(app)

    response = client.post(
        "/api/v1/chat",
        json={
            "message": "Hello",
        },
    )

    assert response.status_code == 429

    assert response.json() == {
        "error": {
            "code": "LLM_RATE_LIMIT",
            "message": (
                "The AI service rate limit or quota was exceeded."
            ),
        },
    }

    app.dependency_overrides.clear()


def test_chat_authentication_error() -> None:

    app.dependency_overrides[
        get_chat_service
    ] = get_authentication_error_chat_service

    client = TestClient(app)

    response = client.post(
        "/api/v1/chat",
        json={
            "message": "Hello",
        },
    )

    assert response.status_code == 401

    assert response.json() == {
        "error": {
            "code": "LLM_AUTHENTICATION",
            "message": (
                "The AI service authentication failed."
            ),
        },
    }

    app.dependency_overrides.clear()


def test_chat_connection_error() -> None:

    app.dependency_overrides[
        get_chat_service
    ] = get_connection_error_chat_service

    client = TestClient(app)

    response = client.post(
        "/api/v1/chat",
        json={
            "message": "Hello",
        },
    )

    assert response.status_code == 503

    assert response.json() == {
        "error": {
            "code": "LLM_CONNECTION",
            "message": (
                "The AI service is currently unavailable."
            ),
        },
    }

    app.dependency_overrides.clear()


def test_chat_unknown_error() -> None:

    app.dependency_overrides[
        get_chat_service
    ] = get_unknown_error_chat_service

    client = TestClient(app)

    response = client.post(
        "/api/v1/chat",
        json={
            "message": "Hello",
        },
    )

    assert response.status_code == 500

    assert response.json() == {
        "error": {
            "code": "LLM_UNKNOWN",
            "message": (
                "An unexpected AI service error occurred."
            ),
        },
    }

    app.dependency_overrides.clear()

