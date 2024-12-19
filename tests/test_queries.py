""" Tests for the queries module. """

import json
from typing import Any, Dict, List
from unittest.mock import patch

import httpx
import pytest

from irrexplorer_cli.irrexplorer import IrrExplorer
from irrexplorer_cli.queries import async_asn_query, process_overlaps


@pytest.mark.asyncio
async def test_asn_query_json_output() -> None:
    """Test ASN query with JSON output."""
    mock_results: Dict[str, List[Any]] = {"directOrigin": [], "overlaps": []}
    mock_sets: Dict[str, Dict[str, Any]] = {"setsPerIrr": {}}

    with (
        patch("irrexplorer_cli.irrexplorer.IrrExplorer.fetch_asn_info", return_value=mock_results),
        patch("irrexplorer_cli.irrexplorer.IrrExplorer.fetch_asn_sets", return_value=mock_sets),
        patch("builtins.print") as mock_print,
    ):
        await async_asn_query("AS12345", "json")
        mock_print.assert_called_with(json.dumps({"asn_info": mock_results, "as_sets": mock_sets}, indent=2), end="\n")


@pytest.mark.asyncio
async def test_asn_query_csv_output() -> None:
    """Test ASN query with CSV output."""
    mock_results: Dict[str, List[Any]] = {"directOrigin": [], "overlaps": []}
    mock_sets: Dict[str, Dict[str, Any]] = {"setsPerIrr": {}}

    with (
        patch("irrexplorer_cli.irrexplorer.IrrExplorer.fetch_asn_info", return_value=mock_results),
        patch("irrexplorer_cli.irrexplorer.IrrExplorer.fetch_asn_sets", return_value=mock_sets),
        patch("builtins.print") as mock_print,
    ):
        await async_asn_query("AS12345", "csv")
        mock_print.assert_any_call("Type,ASN,Prefix,Category,RIR,RPKI_Status,BGP_Origins,IRR_Routes,Messages", end="")


@pytest.mark.asyncio
async def test_process_overlaps_error_handling() -> None:
    """Test error handling in process_overlaps function."""
    explorer = IrrExplorer()
    with patch("irrexplorer_cli.irrexplorer.IrrExplorer.fetch_prefix_info", side_effect=httpx.HTTPError("Test error")):
        await process_overlaps(explorer, "192.0.2.0/24")
    await explorer.close()
