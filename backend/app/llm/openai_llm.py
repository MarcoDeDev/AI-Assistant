from openai import OpenAI

from app.llm.base import BaseLLM
from app.llm.llm_response import LLMResponse
from openai import OpenAI
from openai import OpenAIError

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
    prompt: str,
    ) -> LLMResponse:

        try:

            response = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
            )

        except OpenAIError as error:
            raise RuntimeError(
                "Failed to communicate with OpenAI."
            ) from error

        return LLMResponse(
            text=response.choices[0].message.content or "",
            model=response.model,
            prompt_tokens=response.usage.prompt_tokens,
            completion_tokens=response.usage.completion_tokens,
            total_tokens=response.usage.total_tokens,
            finish_reason=response.choices[0].finish_reason or "unknown",
        )