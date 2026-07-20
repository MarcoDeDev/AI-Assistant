from app.llm.base import BaseLLM
from app.llm.models import LLMResponse


class MockLLM(BaseLLM):

    def generate(
        self,
        prompt: str,
    ) -> LLMResponse:

        return LLMResponse(
            text=f"Mock response: {prompt}",
            model="mock",
            prompt_tokens=0,
            completion_tokens=0,
            total_tokens=0,
            finish_reason="stop",
        )