from collections.abc import Generator

import pytest
from sqlalchemy import create_engine, delete
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.persistence.models.conversation import ConversationModel
from app.persistence.models.message import MessageModel
from app.repositories.sqlalchemy_conversation_repository import (
    SQLAlchemyConversationRepository,
)


@pytest.fixture
def conversation_repository(
) -> Generator[SQLAlchemyConversationRepository, None, None]:
    if settings.test_database_url is None:
        raise RuntimeError(
            "TEST_DATABASE_URL must be configured for integration tests."
        )

    engine = create_engine(
        str(settings.test_database_url),
        pool_pre_ping=True,
    )

    session_factory = sessionmaker(
        bind=engine,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
    )

    session: Session = session_factory()

    try:
        yield SQLAlchemyConversationRepository(session)
    finally:
        session.rollback()
        session.execute(delete(MessageModel))
        session.execute(delete(ConversationModel))
        session.commit()
        session.close()
        engine.dispose()