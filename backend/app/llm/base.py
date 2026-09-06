from abc import ABC, abstractmethod
from collections.abc import Sequence

from app.domain.conversation import Message
from app.llm.llm_response import LLMResponse
from app.llm.tool_definition import ToolDefinition

class BaseLLM(ABC):

    @abstractmethod
    def generate(
        self,
        messages: Sequence[Message],
        *,
        tools: Sequence[ToolDefinition] = (),
    ) -> LLMResponse:
        pass