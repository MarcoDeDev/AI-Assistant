from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.dependencies import get_chat_service
from app.schemas.chat import ChatRequest, ChatResponse
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