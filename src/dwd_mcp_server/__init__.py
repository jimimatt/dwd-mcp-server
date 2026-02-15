"""DWD MCP Server - Weather data from DWD via Bright Sky API."""

from dwd_mcp_server.server import mcp, run_server

__all__ = ["main", "mcp", "run_server"]


def main() -> None:
    """Main entry point for the MCP server."""
    run_server()
