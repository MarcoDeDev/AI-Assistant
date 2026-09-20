import asyncio
from unittest.mock import Mock, patch

from mcp import Client
from pydantic import PostgresDsn

from data_mcp_server.__main__ import main
from data_mcp_server.config import Settings
from data_mcp_server.persistence.database import Database
from data_mcp_server.server import create_server


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
    server = create_server(
        create_test_settings(),
    )

    async def list_tool_names() -> list[str]:
        async with Client(server) as client:
            result = await client.list_tools()

            return [
                tool.name
                for tool in result.tools
            ]

    tool_names = asyncio.run(
        list_tool_names()
    )

    assert tool_names == []


def test_server_lifespan_disposes_database() -> None:
    database = Mock(
        spec=Database,
    )

    with patch(
        "data_mcp_server.application.Database",
        return_value=database,
    ):
        server = create_server(
            create_test_settings(),
        )

        async def connect() -> None:
            async with Client(server):
                pass

        asyncio.run(
            connect()
        )

    database.dispose.assert_called_once_with()


def test_main_starts_streamable_http() -> None:
    runtime_settings = create_test_settings()

    with patch(
        "data_mcp_server.__main__.create_server",
    ) as create_server:
        server = create_server.return_value

        main(runtime_settings)

    create_server.assert_called_once_with(
        runtime_settings,
    )

    server.run.assert_called_once_with(
        transport="streamable-http",
        host="127.0.0.1",
        port=8001,
        streamable_http_path="/mcp",
        stateless_http=True,
        json_response=True,
    )


def test_main_handles_keyboard_interrupt() -> None:
    runtime_settings = create_test_settings()

    with patch(
        "data_mcp_server.__main__.create_server",
    ) as create_server:
        create_server.return_value.run.side_effect = (
            KeyboardInterrupt
        )

        main(runtime_settings)