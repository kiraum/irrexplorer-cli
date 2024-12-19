"""Helper functions for the CLI."""

import ipaddress
import re
from typing import Any, Dict, List

from irrexplorer_cli.models import PrefixInfo, PrefixResult


def validate_prefix_format(prefix_input: str) -> bool:
    """Validate IPv4 or IPv6 prefix format."""
    try:
        ipaddress.ip_network(prefix_input)
        return True
    except ValueError:
        return False


def validate_asn_format(asn_input: str) -> bool:
    """Validate ASN format."""
    asn_pattern = r"^(?:AS|as)?(\d+)$"
    match = re.match(asn_pattern, asn_input)
    if match:
        asn_number = int(match.group(1))
        return 0 <= asn_number <= 4294967295
    return False


def format_prefix_result(result: PrefixInfo, prefix_type: str) -> str:
    """Format a single prefix result for CSV output."""
    prefix_result = PrefixResult(
        prefix=result.prefix,
        categoryOverall=result.categoryOverall,
        rir=result.rir,
        rpkiRoutes=result.rpkiRoutes,
        bgpOrigins=result.bgpOrigins,
        irrRoutes=result.irrRoutes,
        messages=result.messages,
    )

    rpki_status = "NOT_FOUND"
    if prefix_result.rpkiRoutes:
        rpki_status = prefix_result.rpkiRoutes[0].rpkiStatus

    bgp_origins = "|".join(str(asn) for asn in prefix_result.bgpOrigins)

    irr_routes = []
    for db, routes in prefix_result.irrRoutes.items():
        for route in routes:
            irr_routes.append(f"{db}:AS{route.asn}:{route.rpkiStatus}")
    irr_routes_str = "|".join(irr_routes)

    messages = "|".join(msg.text for msg in prefix_result.messages)

    return (
        f"{prefix_type},{prefix_result.prefix},{prefix_result.categoryOverall},"
        f"{prefix_result.rir},{rpki_status},{bgp_origins},{irr_routes_str},{messages}"
    )


def format_direct_origins(as_number: str, results: Dict[str, List[Dict[str, Any]]]) -> None:
    """Format and print direct origin prefixes."""
    for pfx_dict in results.get("directOrigin", []):
        pfx = PrefixInfo(**pfx_dict)
        rpki_status = "NOT_FOUND"
        if pfx.rpkiRoutes:
            rpki_status = pfx.rpkiRoutes[0].rpkiStatus

        bgp_origins = "|".join(str(as_number) for as_number in pfx.bgpOrigins)
        irr_routes = []
        for db, routes in pfx.irrRoutes.items():
            for route in routes:
                irr_routes.append(f"{db}:AS{route.asn}:{route.rpkiStatus}")
        irr_routes_str = "|".join(irr_routes)
        messages = "|".join(msg.text for msg in pfx.messages)

        print(
            f"\nDIRECT,{as_number},{pfx.prefix},{pfx.categoryOverall},{pfx.rir},"
            f"{rpki_status},{bgp_origins},{irr_routes_str},{messages}",
            end="",
        )


def format_overlapping_prefixes(as_number: str, results: Dict[str, List[Dict[str, Any]]]) -> None:
    """Format and print overlapping prefixes."""
    for pfx_dict in results.get("overlaps", []):
        pfx = PrefixInfo(**pfx_dict)
        rpki_status = "NOT_FOUND"
        if pfx.rpkiRoutes:
            rpki_status = pfx.rpkiRoutes[0].rpkiStatus

        bgp_origins = "|".join(str(as_number) for as_number in pfx.bgpOrigins)
        irr_routes = []
        for db, routes in pfx.irrRoutes.items():
            for route in routes:
                irr_routes.append(f"{db}:AS{route.asn}:{route.rpkiStatus}")
        irr_routes_str = "|".join(irr_routes)
        messages = "|".join(msg.text for msg in pfx.messages)

        print(
            f"\nOVERLAP,{as_number},{pfx.prefix},{pfx.categoryOverall},{pfx.rir},"
            f"{rpki_status},{bgp_origins},{irr_routes_str},{messages}",
            end="",
        )


def format_as_sets(as_number: str, sets_data: Dict[str, Dict[str, List[str]]]) -> None:
    """Format and print AS sets."""
    if sets_data and sets_data.get("setsPerIrr"):
        for irr, sets in sets_data["setsPerIrr"].items():
            for as_set in sets:
                print(f"\nSET,{as_number},{as_set},{irr},N/A,N/A,N/A,N/A,N/A", end="")


async def find_least_specific_prefix(direct_overlaps: List[PrefixInfo]) -> str | None:
    """Find the least specific prefix from the overlaps."""
    least_specific = None
    for info in direct_overlaps:
        if "/" in info.prefix:
            _, mask = info.prefix.split("/")
            if least_specific is None or int(mask) < int(least_specific.split("/")[1]):
                least_specific = info.prefix
    return least_specific
