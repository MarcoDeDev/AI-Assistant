import pytest

from app.llm.llm_response import (
    LLMContent,
    LLMResponse,
    TextContent,
)
from app.llm.tool_call import ToolCall
from app.llm.tool_definition import ToolDefinition


def create_response(
    *content: LLMContent,
) -> LLMResponse:
    return LLMResponse(
        content=content,
        model="test-model",
        prompt_tokens=10,
        completion_tokens=5,
        total_tokens=15,
        finish_reason="stop",
    )


def test_response_preserves_content_order_and_derives_views(
) -> None:
    first_text = TextContent(
        text="Before tool call. ",
    )
    tool_call = ToolCall(
        id="call_1",
        name="get_weather",
        arguments={
            "city": "Berlin",
        },
    )
    second_text = TextContent(
        text="After tool call.",
    )

    response = create_response(
        first_text,
        tool_call,
        second_text,
    )

    assert response.content == (
        first_text,
        tool_call,
        second_text,
    )
    assert response.text == (
        "Before tool call. After tool call."
    )
    assert response.tool_calls == (
        tool_call,
    )


def test_tool_call_only_response_has_empty_text(
) -> None:
    tool_call = ToolCall(
        id="call_1",
        name="get_weather",
        arguments={
            "city": "Berlin",
        },
    )

    response = create_response(
        tool_call,
    )

    assert response.text == ""
    assert response.tool_calls == (
        tool_call,
    )


def test_response_rejects_empty_content(
) -> None:
    with pytest.raises(
        ValueError,
        match="LLM response content must not be empty.",
    ):
        create_response()


@pytest.mark.parametrize(
    ("tool_call_id", "tool_name"),
    [
        ("", "get_weather"),
        ("call_1", " "),
    ],
)
def test_tool_call_rejects_empty_identifiers(
    tool_call_id: str,
    tool_name: str,
) -> None:
    with pytest.raises(ValueError):
        ToolCall(
            id=tool_call_id,
            name=tool_name,
            arguments={},
        )


@pytest.mark.parametrize(
    ("tool_name", "description"),
    [
        ("", "Returns the current weather."),
        ("get_weather", " "),
    ],
)
def test_tool_definition_rejects_empty_metadata(
    tool_name: str,
    description: str,
) -> None:
    with pytest.raises(ValueError):
        ToolDefinition(
            name=tool_name,
            description=description,
            parameters={},
        )