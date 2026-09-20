from collections.abc import Generator

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from data_mcp_server.config import load_settings
from data_mcp_server.persistence.database import Database


@pytest.fixture
def database() -> Generator[Database, None, None]:
    settings = load_settings()

    if settings.test_database_url is None:
        raise RuntimeError(
            "MCP_TEST_DATABASE_URL must be configured "
            "for database integration tests."
        )

    database = Database(
        settings.test_database_url,
    )

    try:
        yield database
    finally:
        database.dispose()


def test_database_provides_distinct_read_only_sessions(
    database: Database,
) -> None:
    with database.session() as first_session:
        first_identity = first_session.execute(
            text(
                "SELECT "
                "current_database(), "
                "current_user"
            )
        ).one()

        read_only = first_session.execute(
            text(
                "SHOW default_transaction_read_only"
            )
        ).scalar_one()

    with database.session() as second_session:
        second_identity = second_session.execute(
            text(
                "SELECT "
                "current_database(), "
                "current_user"
            )
        ).one()

    assert isinstance(first_session, Session)
    assert isinstance(second_session, Session)
    assert first_session is not second_session

    assert first_identity == (
        "ai_assistant_test",
        "ai_assistant_mcp_test_reader",
    )
    assert second_identity == first_identity
    assert read_only == "on"