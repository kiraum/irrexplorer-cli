"""Query functions for the CLI tool."""

import json
import logging
from typing import Optional

import httpx
import typer

from irrexplorer_cli.helpers import (
    find_least_specific_prefix,
    format_as_sets,
    format_direct_origins,
    format_overlapping_prefixes,
    format_prefix_result,
)
from irrexplorer_cli.irrexplorer import IrrDisplay, IrrExplorer

logger = logging.getLogger(__name__)


async def process_overlaps(explorer: IrrExplorer, least_specific: str) -> None:
    """Process and print overlapping prefixes."""
    try:
        all_overlaps = await explorer.fetch_prefix_info(least_specific)
        for result in all_overlaps:
            print(format_prefix_result(result, "OVERLAP"))
    except (httpx.HTTPError, ValueError, RuntimeError):
        pass


async def async_prefix_query(pfx: str, output_format: Optional[str] = None, base_url: Optional[str] = None) -> None:
    """Execute asynchronous prefix query and display results."""
    logger.debug("Starting prefix query for: %s", pfx)
    logger.debug("Output format: %s, Base URL: %s", output_format, base_url)

    explorer = IrrExplorer(base_url=base_url) if base_url else IrrExplorer()
    display = IrrDisplay()

    try:
        direct_overlaps = await explorer.fetch_prefix_info(pfx)
        logger.debug("Received %d direct overlaps", len(direct_overlaps))

        if output_format == "json":
            logger.debug("Formatting output as JSON")
            json_data = [result.model_dump() for result in direct_overlaps]
            print(json.dumps(json_data, indent=2))
            return

        if output_format == "csv":
            print("Type,Prefix,Category,RIR,RPKI_Status,BGP_Origins,IRR_Routes,Messages")
            for result in direct_overlaps:
                print(format_prefix_result(result, "DIRECT"))
            least_specific = await find_least_specific_prefix(direct_overlaps)
            if least_specific:
                await process_overlaps(explorer, least_specific)
            return

        await display.display_prefix_info(direct_overlaps)

    except httpx.ConnectError as exc:
        print(
            f"Error: Unable to connect to {base_url or 'default IRR Explorer instance'}. "
            "Please verify the URL is correct and the service is available."
        )
        raise typer.Exit(1) from exc
    finally:
        await explorer.close()


async def async_asn_query(as_number: str, output_format: Optional[str] = None, base_url: Optional[str] = None) -> None:
    """Execute asynchronous ASN query and display results."""
    explorer = IrrExplorer(base_url=base_url) if base_url else IrrExplorer()
    display = IrrDisplay()

    try:
        results = await explorer.fetch_asn_info(as_number)
        sets_data = await explorer.fetch_asn_sets(as_number)

        if output_format == "json":
            combined_data = {"asn_info": results, "as_sets": sets_data}
            print(json.dumps(combined_data, indent=2), end="\n")
        elif output_format == "csv":
            print("Type,ASN,Prefix,Category,RIR,RPKI_Status,BGP_Origins,IRR_Routes,Messages", end="")
            format_direct_origins(as_number, results)
            format_overlapping_prefixes(as_number, results)
            format_as_sets(as_number, sets_data)
            print()
        else:
            await display.display_asn_info(results, as_number, sets_data)
    except httpx.ConnectError as exc:
        print(
            f"Error: Unable to connect to {base_url or 'default IRR Explorer instance'}. "
            "Please verify the URL is correct and the service is available."
        )
        raise typer.Exit(1) from exc
    finally:
        await explorer.close()
