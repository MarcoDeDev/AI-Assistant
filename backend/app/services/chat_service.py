import logging
from time import perf_counter
from uuid import UUID

from app.domain.conversation import (
    Conversation,
    Message,
    MessageRole,
)
from app.llm.base import BaseLLM
from app.repositories.conversation_repository import (
    ConversationRepository,
)
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ConversationHistoryResponse,
    MessageResponse,
)
from app.services.exceptions import ConversationNotFoundError


logger = logging.getLogger(__name__)


class ChatService:

    def __init__(
        self,
        llm: BaseLLM,
        conversation_repository: ConversationRepository,
    ) -> None:
        self._llm = llm
        self._conversation_repository = conversation_repository

    def send_message(
        self,
        request: ChatRequest,
    ) -> ChatResponse:
        start_time = perf_counter()

        conversation = self._get_or_create_conversation(
            request.conversation_id,
        )

        logger.info(
            "Chat request received for conversation %s.",
            conversation.id,
        )

        self._conversation_repository.create_message(
            conversation_id=conversation.id,
            role=MessageRole.USER,
            content=request.message,
        )

        messages = self._conversation_repository.list_messages(
            conversation.id,
        )

        llm_response = self._llm.generate(
            messages,
        )

        self._conversation_repository.create_message(
            conversation_id=conversation.id,
            role=MessageRole.ASSISTANT,
            content=llm_response.text,
        )

        duration = perf_counter() - start_time

        logger.info(
            "Model: %s",
            llm_response.model,
        )
        logger.info(
            "Prompt tokens: %d",
            llm_response.prompt_tokens,
        )
        logger.info(
            "Completion tokens: %d",
            llm_response.completion_tokens,
        )
        logger.info(
            "Total tokens: %d",
            llm_response.total_tokens,
        )
        logger.info(
            "Finish reason: %s",
            llm_response.finish_reason,
        )
        logger.info(
            "Response time: %.3f seconds",
            duration,
        )

        return ChatResponse(
            conversation_id=conversation.id,
            response=llm_response.text,
        )

    def get_conversation_history(
        self,
        conversation_id: UUID,
    ) -> ConversationHistoryResponse:
        conversation = self._get_or_create_conversation(
            conversation_id,
        )

        messages = self._conversation_repository.list_messages(
            conversation.id,
        )

        return ConversationHistoryResponse(
            conversation_id=conversation.id,
            messages=[
                self._to_message_response(message)
                for message in messages
            ],
        )

    @staticmethod
    def _to_message_response(
        message: Message,
    ) -> MessageResponse:
        return MessageResponse(
            id=message.id,
            role=message.role,
            content=message.content,
            created_at=message.created_at,
        )

    def _get_or_create_conversation(
        self,
        conversation_id: UUID | None,
    ) -> Conversation:
        if conversation_id is None:
            return self._conversation_repository.create_conversation()

        conversation = self._conversation_repository.get_conversation(
            conversation_id,
        )

        if conversation is None:
            raise ConversationNotFoundError()

        return conversation