from collections.abc import Sequence

from openai import (
    APIConnectionError,
    AuthenticationError,
    OpenAI,
    OpenAIError,
    RateLimitError,
)

from app.domain.conversation import Message
from app.llm.base import BaseLLM
from app.llm.exceptions import (
    LLMAuthenticationError,
    LLMConnectionError,
    LLMRateLimitError,
    LLMUnknownError,
)
from app.llm.llm_response import LLMResponse


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
            )

        except AuthenticationError as error:
            raise LLMAuthenticationError() from error

        except RateLimitError as error:
            raise LLMRateLimitError() from error

        except APIConnectionError as error:
            raise LLMConnectionError() from error

        except OpenAIError as error:
            raise LLMUnknownError() from error

        return LLMResponse(
            text=response.choices[0].message.content or "",
            model=response.model,
            prompt_tokens=response.usage.prompt_tokens,
            completion_tokens=response.usage.completion_tokens,
            total_tokens=response.usage.total_tokens,
            finish_reason=response.choices[0].finish_reason or "unknown",
        )