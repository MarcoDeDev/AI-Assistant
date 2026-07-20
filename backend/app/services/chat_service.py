import logging

from app.llm.base import BaseLLM
from app.schemas.chat import ChatRequest, ChatResponse
from time import perf_counter

logger = logging.getLogger(__name__)


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

        start_time = perf_counter()

        logger.info("Chat request received.")

        llm_response = self._llm.generate(
            request.message,
        )

        duration = perf_counter() - start_time
 
        logger.info("Model: %s",llm_response.model)

        logger.info("Prompt tokens: %d",llm_response.prompt_tokens)

        logger.info("Completion tokens: %d",llm_response.completion_tokens)

        logger.info("Total tokens: %d",llm_response.total_tokens)

        logger.info("Finish reason: %s",llm_response.finish_reason)

        logger.info("Response time: %.3f seconds", duration)


        return ChatResponse(
            response=llm_response.text,
        )