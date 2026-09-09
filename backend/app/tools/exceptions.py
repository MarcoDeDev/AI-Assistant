class ToolError(Exception):
    pass


class ToolNotFoundError(ToolError):

    def __init__(
        self,
        tool_name: str,
    ) -> None:
        self.tool_name = tool_name

        super().__init__(
            f"Tool '{tool_name}' was not found."
        )


class ToolArgumentsValidationError(ToolError):

    def __init__(
        self,
        tool_call_id: str,
        tool_name: str,
    ) -> None:
        self.tool_call_id = tool_call_id
        self.tool_name = tool_name

        super().__init__(
            f"Arguments for tool '{tool_name}' are invalid."
        )


class ToolExecutionError(ToolError):

    def __init__(
        self,
        tool_call_id: str,
        tool_name: str,
    ) -> None:
        self.tool_call_id = tool_call_id
        self.tool_name = tool_name

        super().__init__(
            f"Execution of tool '{tool_name}' failed."
        )


class DuplicateToolNameError(ToolError):

    def __init__(
        self,
        tool_name: str,
    ) -> None:
        self.tool_name = tool_name

        super().__init__(
            f"Tool name '{tool_name}' is registered more than once."
        )