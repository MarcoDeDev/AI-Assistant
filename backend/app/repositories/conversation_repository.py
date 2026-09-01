from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.conversation import (
    Conversation,
    Message,
    MessageRole,
)


class ConversationRepository(ABC):

    @abstractmethod
    def create_conversation(
        self,
    ) -> Conversation:
        pass

    @abstractmethod
    def get_conversation(
        self,
        conversation_id: UUID,
    ) -> Conversation | None:
        pass

    @abstractmethod
    def create_message(
        self,
        conversation_id: UUID,
        role: MessageRole,
        content: str,
    ) -> Message:
        pass

    @abstractmethod
    def list_messages(
        self,
        conversation_id: UUID,
    ) -> list[Message]:
        pass