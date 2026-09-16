import asyncio
from unittest.mock import patch

from mcp import Client
from pydantic import PostgresDsn

from data_mcp_server.__main__ import main
from data_mcp_server.config import Settings
from data_mcp_server.server import mcp


def create_test_settings() -> Settings:
    return Settings(
        server_host="127.0.0.1",
        server_port=8001,
        server_path="/mcp",
        database_url=PostgresDsn(
            "postgresql+psycopg://reader:"
            "password@localhost:5432/database"
        ),
        test_database_url=PostgresDsn(
            "postgresql+psycopg://test_reader:"
            "password@localhost:5432/test_database"
        ),
    )


def test_server_starts_without_registered_tools() -> None:
    async def list_tool_names() -> list[str]:
        async with Client(mcp) as client:
            result = await client.list_tools()

            return [
                tool.name
                for tool in result.tools
            ]

    tool_names = asyncio.run(
        list_tool_names()
    )

    assert tool_names == []


def test_main_starts_streamable_http() -> None:
    runtime_settings = create_test_settings()

    with patch(
        "data_mcp_server.__main__.mcp.run",
    ) as run:
        main(runtime_settings)

    run.assert_called_once_with(
        transport="streamable-http",
        host="127.0.0.1",
        port=8001,
        streamable_http_path="/mcp",
        stateless_http=True,
        json_response=True,
    )


def test_main_handles_keyboard_interrupt() -> None:
    with patch(
        "data_mcp_server.__main__.mcp.run",
        side_effect=KeyboardInterrupt,
    ):
        main(create_test_settings())