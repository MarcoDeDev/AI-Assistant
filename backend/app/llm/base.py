from abc import ABC, abstractmethod
from collections.abc import Sequence

from app.domain.conversation import Message
from app.llm.llm_response import LLMResponse


class BaseLLM(ABC):

    @abstractmethod
    def generate(
        self,
        messages: Sequence[Message],
    ) -> LLMResponse:
        pass