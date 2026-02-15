"""DWD MCP Server - Weather data from DWD via Bright Sky API."""

from dwd_mcp_server.cli import cli
from dwd_mcp_server.server import mcp, run_server

__all__ = ["cli", "mcp", "run_server"]
