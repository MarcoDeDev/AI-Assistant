from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.domain.conversation import (
    Conversation,
    Message,
    MessageRole,
)
from app.persistence.models.conversation import ConversationModel
from app.persistence.models.message import MessageModel
from app.repositories.conversation_repository import (
    ConversationRepository,
)


class SQLAlchemyConversationRepository(
    ConversationRepository,
):

    def __init__(
        self,
        session: Session,
    ) -> None:
        self._session = session

    def create_conversation(
        self,
    ) -> Conversation:
        model = ConversationModel()

        self._session.add(model)
        self._commit()
        self._session.refresh(model)

        return self._to_conversation(model)

    def get_conversation(
        self,
        conversation_id: UUID,
    ) -> Conversation | None:
        model = self._session.get(
            ConversationModel,
            conversation_id,
        )

        if model is None:
            return None

        return self._to_conversation(model)

    def create_message(
        self,
        conversation_id: UUID,
        role: MessageRole,
        content: str,
    ) -> Message:
        model = MessageModel(
            conversation_id=conversation_id,
            role=role,
            content=content,
        )

        self._session.add(model)

        statement = (
            update(ConversationModel)
            .where(
                ConversationModel.id == conversation_id,
            )
            .values(
                updated_at=func.now(),
            )
        )

        self._session.execute(statement)
        self._commit()
        self._session.refresh(model)

        return self._to_message(model)

    def list_messages(
        self,
        conversation_id: UUID,
    ) -> list[Message]:
        statement = (
            select(MessageModel)
            .where(
                MessageModel.conversation_id == conversation_id,
            )
            .order_by(
                MessageModel.created_at,
                MessageModel.id,
            )
        )

        models = self._session.scalars(
            statement,
        ).all()

        return [
            self._to_message(model)
            for model in models
        ]

    def _commit(self) -> None:
        try:
            self._session.commit()
        except Exception:
            self._session.rollback()
            raise

    @staticmethod
    def _to_conversation(
        model: ConversationModel,
    ) -> Conversation:
        return Conversation(
            id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def _to_message(
        model: MessageModel,
    ) -> Message:
        return Message(
            id=model.id,
            conversation_id=model.conversation_id,
            role=model.role,
            content=model.content,
            created_at=model.created_at,
        )