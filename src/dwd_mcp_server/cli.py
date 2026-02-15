"""CLI for DWD MCP Server."""

import signal
import sys
from types import FrameType

import click

from dwd_mcp_server.server import mcp


def _handle_shutdown(signum: int, _frame: FrameType | None) -> None:
    """Handle shutdown signals gracefully."""
    sig_name = signal.Signals(signum).name
    click.echo(f"\nReceived {sig_name}, shutting down...")
    sys.exit(0)


def _setup_signal_handlers() -> None:
    """Set up handlers for termination signals."""
    signal.signal(signal.SIGINT, _handle_shutdown)
    signal.signal(signal.SIGTERM, _handle_shutdown)


@click.group()
@click.version_option(package_name="dwd-mcp-server")
def cli() -> None:
    """DWD MCP Server - Weather data from DWD via Bright Sky API."""


@cli.command()
def start() -> None:
    """Start the MCP server."""
    _setup_signal_handlers()
    click.echo("Starting DWD MCP Server...", err=True)
    try:
        mcp.run()
    except KeyboardInterrupt:
        click.echo("\nShutting down...", err=True)
        sys.exit(0)


if __name__ == "__main__":
    cli()
