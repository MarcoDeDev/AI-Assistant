from app.llm.base import BaseLLM
from app.schemas.chat import ChatRequest, ChatResponse


class ChatService:

    def __init__(
        self,
        llm: BaseLLM,
    ) -> None:
        self._llm = llm

    def send_message(
        self,
        request: ChatRequest,
    ) -> ChatResponse:

        llm_response = self._llm.generate(
            request.message,
        )

        return ChatResponse(
            response=llm_response.text,
        )