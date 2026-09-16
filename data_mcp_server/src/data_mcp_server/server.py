from importlib.metadata import version

from mcp.server import MCPServer


mcp = MCPServer(
    name="ai-assistant-data",
    title="AI Assistant Data MCP Server",
    description=(
        "Provides read-only conversation data "
        "and analytics tools."
    ),
    version=version(
        "ai-assistant-data-mcp-server"
    ),
)