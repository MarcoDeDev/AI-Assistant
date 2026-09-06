import json
from collections.abc import Sequence

from openai import (
    APIConnectionError,
    AuthenticationError,
    NOT_GIVEN,
    OpenAI,
    OpenAIError,
    RateLimitError,
)
from openai.types.chat import (
    ChatCompletionMessageToolCall,
    ChatCompletionToolParam,
)

from app.domain.conversation import Message
from app.llm.base import BaseLLM
from app.llm.exceptions import (
    LLMAuthenticationError,
    LLMConnectionError,
    LLMRateLimitError,
    LLMUnknownError,
)
from app.llm.llm_response import (
    LLMContent,
    LLMResponse,
    TextContent,
)
from app.llm.tool_call import ToolCall
from app.llm.tool_definition import ToolDefinition


class OpenAILLM(BaseLLM):

    def __init__(
        self,
        client: OpenAI,
        model: str,
    ) -> None:
        self._client = client
        self._model = model

    def generate(
        self,
        messages: Sequence[Message],
        *,
        tools: Sequence[ToolDefinition] = (),
    ) -> LLMResponse:
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {
                        "role": message.role.value,
                        "content": message.content,
                    }
                    for message in messages
                ],
                tools=(
                    [
                        self._to_openai_tool(tool)
                        for tool in tools
                    ]
                    if tools
                    else NOT_GIVEN
                ),
            )

        except AuthenticationError as error:
            raise LLMAuthenticationError() from error

        except RateLimitError as error:
            raise LLMRateLimitError() from error

        except APIConnectionError as error:
            raise LLMConnectionError() from error

        except OpenAIError as error:
            raise LLMUnknownError() from error

        message = response.choices[0].message

        content: list[LLMContent] = []

        if message.content is not None:
            content.append(
                TextContent(
                    text=message.content,
                )
            )

        for tool_call in message.tool_calls or ():
            content.append(
                self._to_tool_call(tool_call)
            )

        if not content:
            content.append(
                TextContent(text="")
            )

        return LLMResponse(
            content=tuple(content),
            model=response.model,
            prompt_tokens=response.usage.prompt_tokens,
            completion_tokens=response.usage.completion_tokens,
            total_tokens=response.usage.total_tokens,
            finish_reason=(
                response.choices[0].finish_reason
                or "unknown"
            ),
        )

    @staticmethod
    def _to_openai_tool(
        tool: ToolDefinition,
    ) -> ChatCompletionToolParam:
        return {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": dict(tool.parameters),
            },
        }

    @staticmethod
    def _to_tool_call(
        tool_call: ChatCompletionMessageToolCall,
    ) -> ToolCall:
        try:
            arguments = json.loads(
                tool_call.function.arguments
            )

            if not isinstance(arguments, dict):
                raise ValueError(
                    "Tool call arguments must be a JSON object."
                )

            return ToolCall(
                id=tool_call.id,
                name=tool_call.function.name,
                arguments=arguments,
            )

        except (TypeError, ValueError) as error:
            raise LLMUnknownError() from error