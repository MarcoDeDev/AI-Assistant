from dataclasses import dataclass

from app.llm.json_types import JSONValue


@dataclass(frozen=True, slots=True)
class ToolResult:
    tool_call_id: str
    output: JSONValue

    def __post_init__(self) -> None:
        if not self.tool_call_id.strip():
            raise ValueError(
                "Tool result call ID must not be empty."
            )