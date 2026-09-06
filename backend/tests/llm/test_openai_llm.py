from datetime import UTC, datetime
from typing import cast
from unittest.mock import Mock
from uuid import uuid4

import pytest
from openai import NOT_GIVEN, OpenAI
from openai.types.chat import (
    ChatCompletion,
    ChatCompletionMessage,
)
from openai.types.chat.chat_completion import Choice
from openai.types.chat.chat_completion_message_function_tool_call import (
    ChatCompletionMessageFunctionToolCall,
    Function,
)
from openai.types.completion_usage import CompletionUsage

from app.domain.conversation import Message, MessageRole
from app.llm.llm_response import TextContent
from app.llm.openai_llm import OpenAILLM
from app.llm.tool_call import ToolCall
from app.llm.tool_definition import ToolDefinition
from app.llm.exceptions import LLMUnknownError


def create_llm(
    response: ChatCompletion,
) -> tuple[OpenAILLM, Mock]:
    client = Mock()
    client.chat.completions.create.return_value = (
        response
    )

    llm = OpenAILLM(
        client=cast(OpenAI, client),
        model="configured-model",
    )

    return llm, client


def test_generate_translates_tools_and_tool_calls(
) -> None:
    openai_response = ChatCompletion(
        id="completion_1",
        choices=[
            Choice(
                index=0,
                finish_reason="tool_calls",
                message=ChatCompletionMessage(
                    role="assistant",
                    content="I will check both cities.",
                    tool_calls=[
                        ChatCompletionMessageFunctionToolCall(
                            id="call_1",
                            type="function",
                            function=Function(
                                name="get_weather",
                                arguments='{"city": "Berlin"}',
                            ),
                        ),
                        ChatCompletionMessageFunctionToolCall(
                            id="call_2",
                            type="function",
                            function=Function(
                                name="get_weather",
                                arguments='{"city": "Rome"}',
                            ),
                        ),
                    ],
                ),
            ),
        ],
        created=0,
        model="returned-model",
        object="chat.completion",
        usage=CompletionUsage(
            prompt_tokens=10,
            completion_tokens=5,
            total_tokens=15,
        ),
    )

    llm, client = create_llm(
        openai_response
    )

    message = Message(
        id=uuid4(),
        conversation_id=uuid4(),
        role=MessageRole.USER,
        content="Compare Berlin and Rome.",
        created_at=datetime.now(UTC),
    )

    tool = ToolDefinition(
        name="get_weather",
        description="Returns the weather for a city.",
        parameters={
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                },
            },
            "required": [
                "city",
            ],
        },
    )

    response = llm.generate(
        messages=(
            message,
        ),
        tools=(
            tool,
        ),
    )

    request = (
        client.chat.completions.create.call_args.kwargs
    )

    assert request["model"] == "configured-model"
    assert request["messages"] == [
        {
            "role": "user",
            "content": "Compare Berlin and Rome.",
        },
    ]
    assert request["tools"] == [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": (
                    "Returns the weather for a city."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                        },
                    },
                    "required": [
                        "city",
                    ],
                },
            },
        },
    ]

    assert response.content == (
        TextContent(
            text="I will check both cities.",
        ),
        ToolCall(
            id="call_1",
            name="get_weather",
            arguments={
                "city": "Berlin",
            },
        ),
        ToolCall(
            id="call_2",
            name="get_weather",
            arguments={
                "city": "Rome",
            },
        ),
    )

    assert response.text == (
        "I will check both cities."
    )
    assert response.tool_calls == (
        ToolCall(
            id="call_1",
            name="get_weather",
            arguments={
                "city": "Berlin",
            },
        ),
        ToolCall(
            id="call_2",
            name="get_weather",
            arguments={
                "city": "Rome",
            },
        ),
    )

    assert response.model == "returned-model"
    assert response.prompt_tokens == 10
    assert response.completion_tokens == 5
    assert response.total_tokens == 15
    assert response.finish_reason == "tool_calls"


def test_generate_omits_tools_when_none_are_available(
) -> None:
    openai_response = ChatCompletion(
        id="completion_1",
        choices=[
            Choice(
                index=0,
                finish_reason="stop",
                message=ChatCompletionMessage(
                    role="assistant",
                    content="Hello.",
                ),
            ),
        ],
        created=0,
        model="returned-model",
        object="chat.completion",
        usage=CompletionUsage(
            prompt_tokens=4,
            completion_tokens=2,
            total_tokens=6,
        ),
    )

    llm, client = create_llm(
        openai_response
    )

    response = llm.generate(
        messages=(),
    )

    request = (
        client.chat.completions.create.call_args.kwargs
    )

    assert request["tools"] is NOT_GIVEN
    assert response.content == (
        TextContent(text="Hello."),
    )
    assert response.text == "Hello."
    assert response.tool_calls == ()


@pytest.mark.parametrize(
    "arguments",
    [
        "not valid JSON",
        '["Berlin"]',
    ],
)
def test_generate_rejects_invalid_tool_arguments(
    arguments: str,
) -> None:
    openai_response = ChatCompletion(
        id="completion_1",
        choices=[
            Choice(
                index=0,
                finish_reason="tool_calls",
                message=ChatCompletionMessage(
                    role="assistant",
                    content=None,
                    tool_calls=[
                        ChatCompletionMessageFunctionToolCall(
                            id="call_1",
                            type="function",
                            function=Function(
                                name="get_weather",
                                arguments=arguments,
                            ),
                        ),
                    ],
                ),
            ),
        ],
        created=0,
        model="returned-model",
        object="chat.completion",
        usage=CompletionUsage(
            prompt_tokens=4,
            completion_tokens=2,
            total_tokens=6,
        ),
    )

    llm, _ = create_llm(
        openai_response
    )

    with pytest.raises(LLMUnknownError):
        llm.generate(
            messages=(),
        )