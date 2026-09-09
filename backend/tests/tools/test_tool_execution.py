import pytest
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from app.llm.json_types import JSONValue
from app.llm.tool_call import ToolCall
from app.tools.exceptions import (
    DuplicateToolNameError,
    ToolArgumentsValidationError,
    ToolExecutionError,
    ToolNotFoundError,
)
from app.tools.executable_tool import ExecutableTool
from app.tools.executor import ToolExecutor
from app.tools.registry import ToolRegistry


class MultiplyArguments(BaseModel):
    model_config = ConfigDict(extra="forbid")

    value: int = Field(gt=0)
    factor: int


class EchoArguments(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str


def multiply(arguments: MultiplyArguments) -> JSONValue:
    return {"result": arguments.value * arguments.factor}


def echo(arguments: EchoArguments) -> JSONValue:
    return arguments.text


def test_executor_selects_tool_by_name_and_preserves_call_id() -> None:
    multiply_tool = ExecutableTool(
        name="multiply",
        description="Multiplies two integers.",
        arguments_model=MultiplyArguments,
        handler=multiply,
    )
    echo_tool = ExecutableTool(
        name="echo",
        description="Returns the supplied text.",
        arguments_model=EchoArguments,
        handler=echo,
    )
    executor = ToolExecutor(ToolRegistry((echo_tool, multiply_tool)))

    result = executor.execute(
        ToolCall(
            id="call_42",
            name="multiply",
            arguments={"value": 4, "factor": 3},
        )
    )

    assert result.tool_call_id == "call_42"
    assert result.output == {"result": 12}


def test_executor_rejects_invalid_arguments_before_handler_execution() -> None:
    received_arguments: list[MultiplyArguments] = []

    def record_execution(arguments: MultiplyArguments) -> JSONValue:
        received_arguments.append(arguments)
        return 0

    tool = ExecutableTool(
        name="multiply",
        description="Multiplies two integers.",
        arguments_model=MultiplyArguments,
        handler=record_execution,
    )
    executor = ToolExecutor(ToolRegistry((tool,)))

    with pytest.raises(ToolArgumentsValidationError) as captured_error:
        executor.execute(
            ToolCall(
                id="call_invalid",
                name="multiply",
                arguments={"value": 0, "factor": 3},
            )
        )

    assert captured_error.value.tool_call_id == "call_invalid"
    assert captured_error.value.tool_name == "multiply"
    assert isinstance(captured_error.value.__cause__, ValidationError)
    assert received_arguments == []


def test_executor_rejects_unknown_tool() -> None:
    executor = ToolExecutor(ToolRegistry(()))

    with pytest.raises(ToolNotFoundError) as captured_error:
        executor.execute(
            ToolCall(
                id="call_unknown",
                name="unknown_tool",
                arguments={},
            )
        )

    assert captured_error.value.tool_name == "unknown_tool"


def test_executor_wraps_handler_exception() -> None:
    def failing_handler(arguments: MultiplyArguments) -> JSONValue:
        raise RuntimeError("External service failed.")

    tool = ExecutableTool(
        name="multiply",
        description="Multiplies two integers.",
        arguments_model=MultiplyArguments,
        handler=failing_handler,
    )
    executor = ToolExecutor(ToolRegistry((tool,)))

    with pytest.raises(ToolExecutionError) as captured_error:
        executor.execute(
            ToolCall(
                id="call_failed",
                name="multiply",
                arguments={"value": 4, "factor": 3},
            )
        )

    assert captured_error.value.tool_call_id == "call_failed"
    assert captured_error.value.tool_name == "multiply"
    assert isinstance(captured_error.value.__cause__, RuntimeError)


def test_registry_rejects_duplicate_tool_names() -> None:
    first_tool = ExecutableTool(
        name="multiply",
        description="First multiplication tool.",
        arguments_model=MultiplyArguments,
        handler=multiply,
    )
    second_tool = ExecutableTool(
        name="multiply",
        description="Second multiplication tool.",
        arguments_model=MultiplyArguments,
        handler=multiply,
    )

    with pytest.raises(DuplicateToolNameError) as captured_error:
        ToolRegistry((first_tool, second_tool))

    assert captured_error.value.tool_name == "multiply"