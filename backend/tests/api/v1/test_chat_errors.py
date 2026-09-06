from collections.abc import Sequence
from datetime import UTC, datetime
from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from app.core.dependencies import get_chat_service
from app.domain.conversation import (
    Conversation,
    Message,
    MessageRole,
)
from app.llm.base import BaseLLM
from app.llm.exceptions import (
    LLMAuthenticationError,
    LLMConnectionError,
    LLMRateLimitError,
    LLMUnknownError,
)
from app.llm.llm_response import LLMResponse, TextContent
from app.main import app
from app.repositories.conversation_repository import (
    ConversationRepository,
)
from app.schemas.chat import ChatRequest
from app.services.chat_service import ChatService
from app.llm.tool_definition import ToolDefinition


class InMemoryConversationRepository(
    ConversationRepository,
):

    def __init__(self) -> None:
        self._conversations: dict[UUID, Conversation] = {}
        self._messages: dict[UUID, list[Message]] = {}

    def create_conversation(
        self,
    ) -> Conversation:
        now = datetime.now(UTC)

        conversation = Conversation(
            id=uuid4(),
            created_at=now,
            updated_at=now,
        )

        self._conversations[conversation.id] = conversation
        self._messages[conversation.id] = []

        return conversation

    def get_conversation(
        self,
        conversation_id: UUID,
    ) -> Conversation | None:
        return self._conversations.get(conversation_id)

    def create_message(
        self,
        conversation_id: UUID,
        role: MessageRole,
        content: str,
    ) -> Message:
        now = datetime.now(UTC)

        message = Message(
            id=uuid4(),
            conversation_id=conversation_id,
            role=role,
            content=content,
            created_at=now,
        )

        self._messages[conversation_id].append(message)

        conversation = self._conversations[conversation_id]

        self._conversations[conversation_id] = Conversation(
            id=conversation.id,
            created_at=conversation.created_at,
            updated_at=now,
        )

        return message

    def list_messages(
        self,
        conversation_id: UUID,
    ) -> list[Message]:
        return sorted(
            self._messages[conversation_id],
            key=lambda message: (
                message.created_at,
                message.id,
            ),
        )


class RateLimitLLM(BaseLLM):

    def generate(
        self,
        messages: Sequence[Message],
        *,
        tools: Sequence[ToolDefinition] = (),
    ) -> LLMResponse:
        raise LLMRateLimitError()


class AuthenticationErrorLLM(BaseLLM):

    def generate(
        self,
        messages: Sequence[Message],
        *,
        tools: Sequence[ToolDefinition] = (),
    ) -> LLMResponse:
        raise LLMAuthenticationError()


class ConnectionErrorLLM(BaseLLM):

    def generate(
        self,
        messages: Sequence[Message],
        *,
        tools: Sequence[ToolDefinition] = (),
    ) -> LLMResponse:
        raise LLMConnectionError()


class UnknownErrorLLM(BaseLLM):

    def generate(
        self,
        messages: Sequence[Message],
        *,
        tools: Sequence[ToolDefinition] = (),
    ) -> LLMResponse:
        raise LLMUnknownError()

class RecordingLLM(BaseLLM):

    def __init__(self) -> None:
        self.requests: list[list[Message]] = []

    def generate(
        self,
        messages: Sequence[Message],
        *,
        tools: Sequence[ToolDefinition] = (),
    ) -> LLMResponse:
        self.requests.append(
            list(messages),
        )

        return LLMResponse(
            content=(
                TextContent(
                    text=(
                        f"Assistant response "
                        f"{len(self.requests)}"
                    ),
                ),
            ),
            model="recording",
            prompt_tokens=0,
            completion_tokens=0,
            total_tokens=0,
            finish_reason="stop",
        )


def create_error_chat_service(
    llm: BaseLLM,
) -> ChatService:
    return ChatService(
        llm=llm,
        conversation_repository=InMemoryConversationRepository(),
    )


def get_rate_limit_chat_service() -> ChatService:
    return create_error_chat_service(
        RateLimitLLM(),
    )


def get_authentication_error_chat_service() -> ChatService:
    return create_error_chat_service(
        AuthenticationErrorLLM(),
    )


def get_connection_error_chat_service() -> ChatService:
    return create_error_chat_service(
        ConnectionErrorLLM(),
    )


def get_unknown_error_chat_service() -> ChatService:
    return create_error_chat_service(
        UnknownErrorLLM(),
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

    
def test_chat_service_persists_conversation_history() -> None:
    repository = InMemoryConversationRepository()
    llm = RecordingLLM()

    chat_service = ChatService(
        llm=llm,
        conversation_repository=repository,
    )

    first_response = chat_service.send_message(
        ChatRequest(
            message="Hello",
        ),
    )

    second_response = chat_service.send_message(
        ChatRequest(
            message="How are you?",
            conversation_id=first_response.conversation_id,
        ),
    )

    assert (
        second_response.conversation_id
        == first_response.conversation_id
    )

    messages = repository.list_messages(
        first_response.conversation_id,
    )

    assert [
        (
            message.role,
            message.content,
        )
        for message in messages
    ] == [
        (
            MessageRole.USER,
            "Hello",
        ),
        (
            MessageRole.ASSISTANT,
            "Assistant response 1",
        ),
        (
            MessageRole.USER,
            "How are you?",
        ),
        (
            MessageRole.ASSISTANT,
            "Assistant response 2",
        ),
    ]

    assert [
        [
            message.content
            for message in request
        ]
        for request in llm.requests
    ] == [
        [
            "Hello",
        ],
        [
            "Hello",
            "Assistant response 1",
            "How are you?",
        ],
    ]


def test_get_conversation_history() -> None:
    repository = InMemoryConversationRepository()
    chat_service = ChatService(
        llm=RecordingLLM(),
        conversation_repository=repository,
    )

    app.dependency_overrides[
        get_chat_service
    ] = lambda: chat_service

    try:
        client = TestClient(app)

        chat_response = client.post(
            "/api/v1/chat",
            json={
                "message": "Hello",
            },
        )

        assert chat_response.status_code == 200

        conversation_id = chat_response.json()[
            "conversation_id"
        ]

        history_response = client.get(
            (
                f"/api/v1/conversations/"
                f"{conversation_id}/messages"
            ),
        )

        assert history_response.status_code == 200

        history = history_response.json()

        assert history["conversation_id"] == conversation_id

        assert [
            (
                message["role"],
                message["content"],
            )
            for message in history["messages"]
        ] == [
            (
                "user",
                "Hello",
            ),
            (
                "assistant",
                "Assistant response 1",
            ),
        ]

        unknown_history_response = client.get(
            (
                f"/api/v1/conversations/"
                f"{uuid4()}/messages"
            ),
        )

        assert unknown_history_response.status_code == 404

        assert unknown_history_response.json() == {
            "error": {
                "code": "CONVERSATION_NOT_FOUND",
                "message": (
                    "The requested conversation was not found."
                ),
            },
        }

    finally:
        app.dependency_overrides.clear()

