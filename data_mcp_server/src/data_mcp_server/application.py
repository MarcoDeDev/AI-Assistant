from collections.abc import (
    AsyncGenerator,
    Callable,
)
from contextlib import (
    AbstractAsyncContextManager,
    asynccontextmanager,
)
from dataclasses import dataclass

from mcp.server import MCPServer

from data_mcp_server.config import Settings
from data_mcp_server.persistence.database import Database


@dataclass(frozen=True, slots=True)
class AppContext:
    database: Database


type AppLifespan = Callable[
    [MCPServer[AppContext]],
    AbstractAsyncContextManager[AppContext],
]


def create_lifespan(
    settings: Settings,
) -> AppLifespan:
    @asynccontextmanager
    async def lifespan(
        _server: MCPServer[AppContext],
    ) -> AsyncGenerator[AppContext]:
        database = Database(
            settings.database_url,
        )

        try:
            yield AppContext(
                database=database,
            )
        finally:
            database.dispose()

    return lifespan