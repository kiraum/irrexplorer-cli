"""Core functionality for IRR Explorer CLI."""

import logging
from typing import Any, Dict, List, Optional, cast

import backoff
import httpx
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from irrexplorer_cli.helpers import find_least_specific_prefix

from .models import PrefixInfo

logger = logging.getLogger(__name__)


class IrrExplorer:
    """IRR Explorer API client for prefix information retrieval."""

    def __init__(self, base_url: str = "https://irrexplorer.nlnog.net") -> None:
        """Initialize IRR Explorer client with base URL."""
        self.base_url = base_url
        self.timeout = httpx.Timeout(300.0)
        self.client = httpx.AsyncClient(timeout=self.timeout)
        self.console = Console()

    @backoff.on_exception(backoff.expo, (httpx.HTTPError, httpx.RequestError), max_tries=3, max_time=300)
    async def fetch_prefix_info(self, prefix: str) -> List[PrefixInfo]:
        """Fetch prefix information from IRR Explorer API."""
        logger.debug("Fetching prefix info for: %s", prefix)
        try:
            url = f"{self.base_url}/api/prefixes/prefix/{prefix}"
            logger.debug("Making API request to: %s", url)
            response = await self.client.get(url)
            response.raise_for_status()
            data = response.json()
            logger.debug("Received response data: %s", data)
            return [PrefixInfo(**item) for item in data]
        except httpx.TimeoutException:
            logger.error("Request timeout for prefix: %s", prefix)
            return []

    @backoff.on_exception(backoff.expo, (httpx.HTTPError, httpx.RequestError), max_tries=3, max_time=300)
    async def fetch_asn_info(self, asn: str) -> Dict[str, Any]:
        """Fetch prefix information for an AS number."""
        try:
            url = f"{self.base_url}/api/prefixes/asn/{asn}"
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                data = cast(Dict[str, Any], response.json())
                if not data:
                    return {"directOrigin": [], "overlaps": []}
                return data
        except httpx.TimeoutException:
            self.console.print(
                f"[yellow]Request timed out while fetching info for {asn}. The server might be busy.[/yellow]"
            )
            return {"directOrigin": [], "overlaps": []}

    @backoff.on_exception(backoff.expo, (httpx.HTTPError, httpx.RequestError), max_tries=3, max_time=300)
    async def fetch_asn_sets(self, asn: str) -> Dict[str, Any]:
        """Fetch AS sets information for an AS number."""
        try:
            url = f"{self.base_url}/api/sets/member-of/{asn}"
            response = await self.client.get(url)
            response.raise_for_status()
            data = cast(Dict[str, Any], response.json())
            if not data:
                return {"setsPerIrr": {}}
            return data
        except httpx.TimeoutException:
            self.console.print(
                f"[yellow]Request timed out while fetching AS sets for {asn}. The server might be busy.[/yellow]"
            )
            return {"setsPerIrr": {}}

    async def close(self) -> None:
        """Close the HTTP client connection."""
        await self.client.aclose()


class IrrDisplay:
    """Display handler for IRR Explorer prefix information."""

    def __init__(self) -> None:
        """Initialize display handler with Rich console."""
        self.console = Console()

    async def create_prefix_panel(self, info: PrefixInfo) -> Panel:
        """Create Rich panel with prefix information."""
        table = Table(show_header=True, header_style="bold cyan", expand=True)
        table.add_column("Property")
        table.add_column("Value")

        # Add basic info asynchronously
        await self.add_basic_info(table, info)
        await self.add_bgp_origins(table, info)
        await self.add_rpki_routes(table, info)
        await self.add_irr_routes(table, info)
        await self.add_status(table, info)
        await self.add_messages(table, info)

        return Panel(
            table,
            title=f"[bold]{info.prefix}[/bold]",
            expand=False,
            border_style=await self.get_status_style(info.categoryOverall),
        )

    async def sort_and_group_panels(self, prefix_infos: List[PrefixInfo]) -> List[Panel]:
        """Sort and group prefix information panels by status category."""
        status_groups: Dict[str, List[Panel]] = {"success": [], "warning": [], "error": [], "danger": [], "info": []}

        sorted_infos = sorted(prefix_infos, key=lambda x: (-int(x.prefix.split("/")[1]), x.categoryOverall))

        for info in sorted_infos:
            panel = await self.create_prefix_panel(info)
            status_groups[info.categoryOverall].append(panel)

        return [
            panel for status in ["success", "warning", "error", "danger", "info"] for panel in status_groups[status]
        ]

    async def add_basic_info(self, table: Table, info: PrefixInfo) -> None:
        """Add basic prefix information to the display table."""
        table.add_row("Prefix", info.prefix)
        table.add_row("RIR", info.rir)

    async def add_bgp_origins(self, table: Table, info: PrefixInfo) -> None:
        """Add BGP origin information to the display table."""
        bgp_origins = ", ".join(f"AS{asn}" for asn in info.bgpOrigins) if info.bgpOrigins else "None"
        table.add_row("BGP Origins", bgp_origins)

    async def add_rpki_routes(self, table: Table, info: PrefixInfo) -> None:
        """Add RPKI route information to the display table."""
        if info.rpkiRoutes:
            rpki_rows = [
                f"AS{route.asn} (MaxLength: {route.rpkiMaxLength}, Status: {route.rpkiStatus})"
                for route in info.rpkiRoutes
            ]
            table.add_row("RPKI Routes", "\n".join(rpki_rows))

    async def add_irr_routes(self, table: Table, info: PrefixInfo) -> None:
        """Add IRR route information to the display table."""
        if info.irrRoutes:
            irr_rows = [
                f"{db}: AS{route.asn} ({route.rpkiStatus})" for db, routes in info.irrRoutes.items() for route in routes
            ]
            if irr_rows:
                table.add_row("IRR Routes", "\n".join(irr_rows))

    async def add_status(self, table: Table, info: PrefixInfo) -> None:
        """Add status information to the display table."""
        status_style = await self.get_status_style(info.categoryOverall)
        table.add_row("Status", Text(info.categoryOverall, style=status_style))

    async def add_messages(self, table: Table, info: PrefixInfo) -> None:
        """Add message information to the display table."""
        if info.messages:
            messages = "\n".join(f"• {msg.text}" for msg in info.messages)
            table.add_row("Messages", messages)

    async def get_status_style(self, category: str) -> str:
        """Get Rich style color based on status category."""
        return {"success": "green", "warning": "yellow", "error": "red", "danger": "red", "info": "blue"}.get(
            category, "white"
        )

    async def display_prefix_info(self, direct_overlaps: List[PrefixInfo]) -> None:
        """Display prefix information in Rich panels."""
        logger.debug("Displaying prefix info for %d overlaps", len(direct_overlaps))
        if not direct_overlaps:
            logger.debug("No prefix information found")
            self.console.print("[yellow]No prefix information found[/yellow]")
            return

        await self.display_direct_overlaps(direct_overlaps)
        least_specific = await find_least_specific_prefix(direct_overlaps)
        if least_specific:
            await self.display_all_overlaps(least_specific)

    async def display_direct_overlaps(self, direct_overlaps: List[PrefixInfo]) -> None:
        """Display directly overlapping prefixes."""
        if not direct_overlaps:
            self.console.print("[yellow]No prefix information found[/yellow]")
            return

        direct_panels = await self.sort_and_group_panels(direct_overlaps)
        direct_columns = Columns(direct_panels, equal=True, expand=True)
        self.console.print(
            Panel(
                direct_columns,
                title=f"[bold]Directly overlapping prefixes of {direct_overlaps[0].prefix}[/bold]",
                expand=False,
            )
        )

    async def display_all_overlaps(self, least_specific: str) -> None:
        """Display all overlaps for least specific prefix."""
        try:
            explorer = IrrExplorer()
            all_overlaps = await explorer.fetch_prefix_info(least_specific)
            all_panels = await self.sort_and_group_panels(all_overlaps)
            all_columns = Columns(all_panels, equal=True, expand=True)

            self.console.print("\n")
            self.console.print(
                Panel(
                    all_columns,
                    title=f"[bold]All overlaps of least specific match {least_specific}[/bold]",
                    expand=False,
                )
            )
            await explorer.close()
        except (httpx.HTTPError, ValueError, RuntimeError) as e:
            self.console.print(f"[red]Error fetching overlaps for {least_specific}: {str(e)}[/red]")
        finally:
            await explorer.close()

    def get_rpki_status(self, prefix: Dict[str, Any]) -> str:
        """Extract RPKI status from prefix info."""
        if prefix.get("rpkiRoutes"):
            return cast(str, prefix["rpkiRoutes"][0]["rpkiStatus"])
        return "UNKNOWN"

    async def display_asn_info(
        self, data: Dict[str, Any], asn: str, sets_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Display AS query results with rich formatting."""
        if not data:
            self.console.print(f"[yellow]No information found for AS{asn}[/yellow]")
            return

        await self.display_direct_origins(data, asn)
        await self.display_overlaps(data, asn)
        self.display_as_sets(sets_data, asn)

    async def display_direct_origins(self, data: Dict[str, Any], asn: str) -> None:
        """Display direct origin prefixes."""
        if not data.get("directOrigin"):
            return

        try:
            direct_infos = [PrefixInfo(**prefix) for prefix in data["directOrigin"]]
        except (ValueError, TypeError):
            return

        direct_panels = await self.sort_and_group_panels(direct_infos)
        direct_columns = Columns(direct_panels, equal=True, expand=True)
        self.console.print(
            Panel(
                direct_columns,
                title=f"[bold]Prefixes directly originated by {asn}[/bold]",
                expand=False,
            )
        )

    async def display_overlaps(self, data: Dict[str, Any], asn: str) -> None:
        """Display overlapping prefixes."""
        if not data.get("overlaps"):
            return

        try:
            overlap_infos = [PrefixInfo(**prefix) for prefix in data["overlaps"]]
        except (ValueError, TypeError):
            return

        overlap_panels = await self.sort_and_group_panels(overlap_infos)
        if overlap_panels:
            self.console.print("\n")
            overlap_columns = Columns(overlap_panels, equal=True, expand=True)
            self.console.print(
                Panel(
                    overlap_columns,
                    title=f"[bold]Overlapping prefixes related to {asn}[/bold]",
                    expand=False,
                )
            )
            self.console.print("\n")

    def display_as_sets(self, sets_data: Optional[Dict[str, Any]], asn: str) -> None:
        """Display AS sets information."""
        if sets_data and sets_data.get("setsPerIrr"):
            sets_panels = []
            for irr, sets in sets_data["setsPerIrr"].items():
                table = Table(show_header=False, expand=True)
                for as_set in sets:
                    table.add_row(as_set)
                panel = Panel(table, title=f"[bold]{irr}[/bold]", border_style="blue")
                sets_panels.append(panel)

            sets_columns = Columns(sets_panels, equal=True, expand=True)
            self.console.print(
                Panel(
                    sets_columns,
                    title=f"[bold]AS Sets including {asn}[/bold]",
                    expand=False,
                )
            )
