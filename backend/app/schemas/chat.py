from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.domain.conversation import MessageRole


class ChatRequest(BaseModel):
    message: str
    conversation_id: UUID | None = None


class ChatResponse(BaseModel):
    conversation_id: UUID
    response: str


class MessageResponse(BaseModel):
    id: UUID
    role: MessageRole
    content: str
    created_at: datetime


class ConversationHistoryResponse(BaseModel):
    conversation_id: UUID
    messages: list[MessageResponse]