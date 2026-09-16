from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    server_host: str = "127.0.0.1"
    server_port: int = Field(
        default=8001,
        ge=1,
        le=65535,
    )
    server_path: str = "/mcp"

    database_url: PostgresDsn
    test_database_url: PostgresDsn | None = None

    model_config = SettingsConfigDict(
        env_prefix="MCP_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        frozen=True,
    )


def load_settings() -> Settings:
    return Settings()  # pyright: ignore[reportCallIssue]