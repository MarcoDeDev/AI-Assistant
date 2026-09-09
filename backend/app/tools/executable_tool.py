from collections.abc import Callable
from dataclasses import dataclass, field

from pydantic import BaseModel

from app.llm.json_types import JSONValue
from app.llm.tool_definition import ToolDefinition


@dataclass(frozen=True, slots=True)
class ExecutableTool[ArgumentsT: BaseModel]:
    name: str
    description: str
    arguments_model: type[ArgumentsT]
    handler: Callable[
        [ArgumentsT],
        JSONValue,
    ] = field(repr=False)
    definition: ToolDefinition = field(
        init=False,
    )

    def __post_init__(self) -> None:
        definition = ToolDefinition(
            name=self.name,
            description=self.description,
            parameters=(
                self.arguments_model.model_json_schema()
            ),
        )

        object.__setattr__(
            self,
            "definition",
            definition,
        )

    def execute(
        self,
        arguments: ArgumentsT,
    ) -> JSONValue:
        return self.handler(arguments)