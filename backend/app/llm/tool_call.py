from collections.abc import Mapping
from dataclasses import dataclass

from app.llm.json_types import JSONValue


@dataclass(frozen=True, slots=True)
class ToolCall:
    id: str
    name: str
    arguments: Mapping[str, JSONValue]

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError(
                "Tool call ID must not be empty."
            )

        if not self.name.strip():
            raise ValueError(
                "Tool call name must not be empty."
            )