"""Command-line interface for IRR Explorer queries."""

import asyncio
import logging
from importlib.metadata import version
from typing import Optional

import typer
from rich.console import Console

from irrexplorer_cli.helpers import validate_asn_format, validate_prefix_format, validate_url_format
from irrexplorer_cli.queries import async_asn_query, async_prefix_query

__version__ = version("irrexplorer-cli")

CTX_OPTION = typer.Option(None, hidden=True)
app = typer.Typer(
    help="CLI tool to query IRR Explorer data for prefix information",
    no_args_is_help=True,
    context_settings={"help_option_names": ["-h", "--help"]},
)
console = Console()
logger = logging.getLogger(__name__)


def setup_logging(debug: bool) -> None:
    """Configure logging based on debug flag."""
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=log_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # set httpx logger level based on debug flag
    httpx_logger = logging.getLogger("httpx")
    httpx_logger.setLevel(logging.DEBUG if debug else logging.WARNING)


def version_display(display_version: bool) -> None:
    """Display version information and exit."""
    if display_version:
        print(f"[bold]IRR Explorer CLI[/bold] version: {__version__}")
        raise typer.Exit()


@app.callback()
def callback(
    ctx: typer.Context,
    _: bool = typer.Option(None, "--version", "-v", callback=version_display, is_eager=True),
    base_url: Optional[str] = typer.Option(None, "--url", "-u", help="Base URL for IRR Explorer API"),
    debug: bool = typer.Option(False, "--debug", "-d", help="Enable debug logging"),
) -> None:
    """Query IRR Explorer for prefix information."""
    ctx.ensure_object(dict)
    ctx.obj["base_url"] = base_url
    setup_logging(debug)
    logger.debug("CLI initialized with base_url: %s", base_url)


@app.command(no_args_is_help=True)
def prefix(
    ctx: typer.Context,
    prefix_query: str = typer.Argument(None, help="Prefix to query (e.g., 193.0.0.0/21)"),
    output_format: Optional[str] = typer.Option(None, "--format", "-f", help="Output format (json or csv)"),
) -> None:
    """Query IRR Explorer for prefix information."""
    base_url: Optional[str] = ctx.obj.get("base_url")
    if not prefix_query:
        if ctx:
            typer.echo(ctx.get_help())
        raise typer.Exit()

    if not validate_prefix_format(prefix_query):
        typer.echo(f"Error: Invalid prefix format: {prefix_query}")
        raise typer.Exit(1)

    if base_url and not validate_url_format(base_url):
        typer.echo(f"Error: Invalid URL format: {base_url}")
        raise typer.Exit(1)

    asyncio.run(async_prefix_query(prefix_query, output_format, base_url))


@app.command(no_args_is_help=True)
def asn(
    ctx: typer.Context,
    asn_query: str = typer.Argument(None, help="AS number to query (e.g., AS2111, as2111, or 2111)"),
    output_format: Optional[str] = typer.Option(None, "--format", "-f", help="Output format (json or csv)"),
) -> None:
    """Query IRR Explorer for AS number information."""
    base_url: Optional[str] = ctx.obj.get("base_url")
    if not asn_query:
        if ctx:
            typer.echo(ctx.get_help())
        raise typer.Exit()

    if isinstance(asn_query, str):
        if not asn_query.upper().startswith("AS"):
            asn_query = f"AS{asn_query}"
        else:
            asn_query = f"AS{asn_query[2:]}"

    if not validate_asn_format(asn_query):
        typer.echo(f"Error: Invalid ASN format: {asn_query}")
        raise typer.Exit(1)

    if base_url and not validate_url_format(base_url):
        typer.echo(f"Error: Invalid URL format: {base_url}")
        raise typer.Exit(1)

    asyncio.run(async_asn_query(asn_query, output_format, base_url))
