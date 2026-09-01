from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from app.core.dependencies import get_chat_service
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ConversationHistoryResponse,
)
from app.services.chat_service import ChatService

router = APIRouter(
    tags=["Chat"],
)

@router.post(
    "/chat",
    response_model=ChatResponse,
)
def chat(
    request: ChatRequest,
    chat_service: Annotated[
        ChatService,
        Depends(get_chat_service),
    ],
) -> ChatResponse:

    return chat_service.send_message(
        request,
    )

@router.get(
    "/conversations/{conversation_id}/messages",
    response_model=ConversationHistoryResponse,
)
def get_conversation_history(
    conversation_id: UUID,
    chat_service: Annotated[
        ChatService,
        Depends(get_chat_service),
    ],
) -> ConversationHistoryResponse:
    return chat_service.get_conversation_history(
        conversation_id,
    )