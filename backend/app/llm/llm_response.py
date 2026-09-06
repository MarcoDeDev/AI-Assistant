from dataclasses import dataclass

from app.llm.tool_call import ToolCall


@dataclass(frozen=True, slots=True)
class TextContent:
    text: str


type LLMContent = TextContent | ToolCall


@dataclass(frozen=True, slots=True)
class LLMResponse:
    content: tuple[LLMContent, ...]

    model: str

    prompt_tokens: int

    completion_tokens: int

    total_tokens: int

    finish_reason: str

    def __post_init__(self) -> None:
        if not self.content:
            raise ValueError(
                "LLM response content must not be empty."
            )

    @property
    def text(self) -> str:
        return "".join(
            item.text
            for item in self.content
            if isinstance(item, TextContent)
        )

    @property
    def tool_calls(self) -> tuple[ToolCall, ...]:
        return tuple(
            item
            for item in self.content
            if isinstance(item, ToolCall)
        )