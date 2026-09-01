from functools import lru_cache
from typing import Annotated

from openai import OpenAI
from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.config import settings
from app.llm.base import BaseLLM
from app.llm.openai_llm import OpenAILLM
from app.persistence.database import get_db_session
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.sqlalchemy_conversation_repository import (
    SQLAlchemyConversationRepository,
)
from app.services.chat_service import ChatService


@lru_cache
def get_openai_client() -> OpenAI:

    return OpenAI(
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
    )


@lru_cache
def get_llm() -> BaseLLM:

    return OpenAILLM(
        client=get_openai_client(),
        model=settings.openai_model,
    )

def get_conversation_repository(
    session: Annotated[
        Session,
        Depends(get_db_session),
    ],
) -> ConversationRepository:
    return SQLAlchemyConversationRepository(
        session=session,
    )

def get_chat_service(
    conversation_repository: Annotated[
        ConversationRepository,
        Depends(get_conversation_repository),
    ],
) -> ChatService:
    return ChatService(
        llm=get_llm(),
        conversation_repository=conversation_repository,
    )