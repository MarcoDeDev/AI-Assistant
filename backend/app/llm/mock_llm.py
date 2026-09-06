from collections.abc import Sequence

from app.domain.conversation import Message, MessageRole
from app.llm.base import BaseLLM
from app.llm.llm_response import LLMResponse, TextContent
from app.llm.tool_definition import ToolDefinition


class MockLLM(BaseLLM):

    def generate(
        self,
        messages: Sequence[Message],
        *,
        tools: Sequence[ToolDefinition] = (),
    ) -> LLMResponse:
        latest_user_message = next(
            (
                message
                for message in reversed(messages)
                if message.role == MessageRole.USER
            ),
            None,
        )

        prompt = (
            latest_user_message.content
            if latest_user_message is not None
            else ""
        )

        return LLMResponse(
            content=(
                TextContent(
                    text=f"Mock response: {prompt}",
                ),
            ),
            model="mock",
            prompt_tokens=0,
            completion_tokens=0,
            total_tokens=0,
            finish_reason="stop",
        )