from collections.abc import Mapping, Sequence
from types import MappingProxyType
from typing import Any

from app.tools.exceptions import (
    DuplicateToolNameError,
    ToolNotFoundError,
)
from app.tools.executable_tool import ExecutableTool


class ToolRegistry:
    __slots__ = (
        "_tools",
    )

    def __init__(
        self,
        tools: Sequence[ExecutableTool[Any]],
    ) -> None:
        tools_by_name: dict[
            str,
            ExecutableTool[Any],
        ] = {}

        for tool in tools:
            if tool.name in tools_by_name:
                raise DuplicateToolNameError(
                    tool.name
                )

            tools_by_name[tool.name] = tool

        self._tools: Mapping[
            str,
            ExecutableTool[Any],
        ] = MappingProxyType(
            tools_by_name
        )

    def get(
        self,
        tool_name: str,
    ) -> ExecutableTool[Any]:
        tool = self._tools.get(
            tool_name
        )

        if tool is None:
            raise ToolNotFoundError(
                tool_name
            )

        return tool