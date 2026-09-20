from importlib.metadata import version

from mcp.server import MCPServer

from data_mcp_server.application import (
    AppContext,
    create_lifespan,
)
from data_mcp_server.config import Settings


def create_server(
    settings: Settings,
) -> MCPServer[AppContext]:
    return MCPServer(
        name="ai-assistant-data",
        title="AI Assistant Data MCP Server",
        description=(
            "Provides read-only conversation data "
            "and analytics tools."
        ),
        version=version(
            "ai-assistant-data-mcp-server"
        ),
        lifespan=create_lifespan(settings),
    )