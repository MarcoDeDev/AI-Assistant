from data_mcp_server.config import Settings, load_settings
from data_mcp_server.server import mcp


def main(
    settings: Settings | None = None,
) -> None:
    runtime_settings = (
        settings
        if settings is not None
        else load_settings()
    )

    try:
        mcp.run(
            transport="streamable-http",
            host=runtime_settings.server_host,
            port=runtime_settings.server_port,
            streamable_http_path=runtime_settings.server_path,
            stateless_http=True,
            json_response=True,
        )
    except KeyboardInterrupt:
        return


if __name__ == "__main__":
    main()