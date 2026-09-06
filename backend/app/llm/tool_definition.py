from collections.abc import Mapping
from dataclasses import dataclass

from app.llm.json_types import JSONValue


@dataclass(frozen=True, slots=True)
class ToolDefinition:
    name: str
    description: str
    parameters: Mapping[str, JSONValue]

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError(
                "Tool definition name must not be empty."
            )

        if not self.description.strip():
            raise ValueError(
                "Tool definition description must not be empty."
            )