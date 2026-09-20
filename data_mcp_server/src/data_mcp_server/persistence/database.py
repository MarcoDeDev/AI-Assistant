from collections.abc import Generator
from contextlib import contextmanager

from pydantic import PostgresDsn
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker


class Database:
    __slots__ = (
        "_engine",
        "_session_factory",
    )

    def __init__(
        self,
        database_url: PostgresDsn,
    ) -> None:
        self._engine: Engine = create_engine(
            str(database_url),
            pool_pre_ping=True,
        )

        self._session_factory = sessionmaker(
            bind=self._engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
        )

    @contextmanager
    def session(
        self,
    ) -> Generator[Session, None, None]:
        session = self._session_factory()

        try:
            yield session
        finally:
            session.rollback()
            session.close()

    def dispose(self) -> None:
        self._engine.dispose()