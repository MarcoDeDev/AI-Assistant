from abc import ABC
from abc import abstractmethod

from app.llm.llm_response import LLMResponse


class BaseLLM(ABC):

    @abstractmethod
    def generate(
        self,
        prompt: str,
    ) -> LLMResponse:
        pass