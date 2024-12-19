"""Command-line interface for IRR Explorer queries."""

import asyncio
from importlib.metadata import version

import typer
from click import Context
from rich.console import Console

from irrexplorer_cli.helpers import validate_asn_format, validate_prefix_format
from irrexplorer_cli.queries import async_asn_query, async_prefix_query

__version__ = version("irrexplorer-cli")

CTX_OPTION = typer.Option(None, hidden=True)
app = typer.Typer(
    help="CLI tool to query IRR Explorer data for prefix information",
    no_args_is_help=True,
    context_settings={"help_option_names": ["-h", "--help"]},
)
console = Console()


def version_display(display_version: bool) -> None:
    """Display version information and exit."""
    if display_version:
        print(f"[bold]IRR Explorer CLI[/bold] version: {__version__}")
        raise typer.Exit()


@app.callback()
def callback(
    _: bool = typer.Option(None, "--version", "-v", callback=version_display, is_eager=True),
) -> None:
    """Query IRR Explorer for prefix information."""


@app.command(no_args_is_help=True)
def prefix(
    prefix_query: str = typer.Argument(None, help="Prefix to query (e.g., 193.0.0.0/21)"),
    output_format: str = typer.Option(None, "--format", "-f", help="Output format (json or csv)"),
    ctx: Context = CTX_OPTION,
) -> None:
    """Query IRR Explorer for prefix information."""
    if not prefix_query:
        if ctx:
            typer.echo(ctx.get_help())
        raise typer.Exit()

    if not validate_prefix_format(prefix_query):
        typer.echo(f"Error: Invalid prefix format: {prefix_query}")
        raise typer.Exit(1)

    asyncio.run(async_prefix_query(prefix_query, output_format))


@app.command()
def asn(
    asn_query: str = typer.Argument(None, help="AS number to query (e.g., AS2111, as2111, or 2111)"),
    output_format: str = typer.Option(None, "--format", "-f", help="Output format (json or csv)"),
    ctx: Context = CTX_OPTION,
) -> None:
    """Query IRR Explorer for AS number information."""
    if not asn_query:
        if ctx:
            typer.echo(ctx.get_help())
        raise typer.Exit()

    if not validate_asn_format(asn_query):
        typer.echo(f"Error: Invalid ASN format: {asn_query}")
        raise typer.Exit(1)

    if not asn_query.upper().startswith("AS"):
        asn_query = f"AS{asn_query}"
    else:
        asn_query = f"AS{asn_query[2:]}"

    asyncio.run(async_asn_query(asn_query, output_format))
