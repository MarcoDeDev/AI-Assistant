from uuid import uuid4

from app.repositories.sqlalchemy_conversation_repository import (
    SQLAlchemyConversationRepository,
)


def test_create_and_get_conversation(
    conversation_repository: SQLAlchemyConversationRepository,
) -> None:
    created_conversation = (
        conversation_repository.create_conversation()
    )

    loaded_conversation = (
        conversation_repository.get_conversation(
            created_conversation.id,
        )
    )

    assert loaded_conversation == created_conversation
    assert loaded_conversation is not None
    assert loaded_conversation.created_at.tzinfo is not None
    assert loaded_conversation.updated_at.tzinfo is not None

    unknown_conversation = (
        conversation_repository.get_conversation(
            uuid4(),
        )
    )

    assert unknown_conversation is None