from pydantic import ValidationError

from app.llm.tool_call import ToolCall
from app.tools.exceptions import (
    ToolArgumentsValidationError,
    ToolExecutionError,
)
from app.tools.registry import ToolRegistry
from app.tools.tool_result import ToolResult


class ToolExecutor:
    __slots__ = (
        "_registry",
    )

    def __init__(
        self,
        registry: ToolRegistry,
    ) -> None:
        self._registry = registry

    def execute(
        self,
        tool_call: ToolCall,
    ) -> ToolResult:
        tool = self._registry.get(
            tool_call.name
        )

        try:
            arguments = (
                tool.arguments_model.model_validate(
                    tool_call.arguments
                )
            )

        except ValidationError as error:
            raise ToolArgumentsValidationError(
                tool_call_id=tool_call.id,
                tool_name=tool_call.name,
            ) from error

        try:
            output = tool.execute(
                arguments
            )

        except Exception as error:
            raise ToolExecutionError(
                tool_call_id=tool_call.id,
                tool_name=tool_call.name,
            ) from error

        return ToolResult(
            tool_call_id=tool_call.id,
            output=output,
        )