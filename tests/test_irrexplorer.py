"""Test suite for IRR Explorer core functionality."""

from typing import Any
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from irrexplorer_cli.irrexplorer import IrrDisplay, IrrExplorer
from irrexplorer_cli.models import PrefixInfo
from tests.fixtures import COMMON_ASN_DATA, COMMON_PREFIX_INFO, COMMON_SETS_DATA, create_basic_prefix_info


@pytest.mark.asyncio
async def test_fetch_prefix_info() -> None:
    """Test successful prefix information retrieval."""
    explorer = IrrExplorer()
    result = await explorer.fetch_prefix_info("5.57.21.0/24")
    assert isinstance(result, list)
    assert all(isinstance(item, PrefixInfo) for item in result)
    await explorer.close()


@pytest.mark.asyncio
async def test_display_prefix_info() -> None:
    """Test prefix information display formatting."""
    display = IrrDisplay()
    test_data = [create_basic_prefix_info(prefix="5.57.21.0/24", rpkiRoutes=[])]
    await display.display_prefix_info(test_data)


@pytest.mark.asyncio
async def test_create_prefix_panel() -> None:
    """Test panel creation with prefix information."""
    display = IrrDisplay()
    test_info = create_basic_prefix_info(prefix="5.57.21.0/24", rpkiRoutes=[])
    panel = await display.create_prefix_panel(test_info)
    assert panel is not None


@pytest.mark.asyncio
async def test_display_prefix_info_least_specific_error() -> None:
    """Test error handling for least specific prefix display."""
    display = IrrDisplay()
    test_data = [create_basic_prefix_info(prefix="5.57.0.0/16", rpkiRoutes=[])]

    with patch("irrexplorer_cli.irrexplorer.IrrExplorer") as mock_explorer_class:
        mock_instance = mock_explorer_class.return_value
        mock_instance.fetch_prefix_info = AsyncMock(side_effect=ValueError("Test error"))
        mock_instance.close = AsyncMock()

        with patch.object(display.console, "print") as mock_print:
            await display.display_prefix_info(test_data)
            mock_print.assert_called_with("[red]Error fetching overlaps for 5.57.0.0/16: Test error[/red]")


@pytest.mark.asyncio
async def test_fetch_asn_sets() -> None:
    """Test AS sets information retrieval."""
    explorer = IrrExplorer()
    result = await explorer.fetch_asn_sets("AS202196")
    assert isinstance(result, dict)
    await explorer.close()


@pytest.mark.asyncio
async def test_display_status_categories() -> None:
    """Test status category display styles."""
    display = IrrDisplay()
    styles = {
        "success": await display.get_status_style("success"),
        "warning": await display.get_status_style("warning"),
        "error": await display.get_status_style("error"),
    }
    assert all(isinstance(style, str) for style in styles.values())


@pytest.mark.asyncio
async def test_asn_info_display() -> None:
    """Test ASN info display with complete data."""
    display = IrrDisplay()
    await display.display_asn_info(COMMON_ASN_DATA, "AS12345", COMMON_SETS_DATA)


@pytest.mark.asyncio
async def test_display_overlaps() -> None:
    """Test overlaps display functionality."""
    display = IrrDisplay()

    # Create data using the fixture but override specific fields
    overlap_info = COMMON_PREFIX_INFO.copy()
    overlap_info.update({"categoryOverall": "warning", "rpkiRoutes": [], "irrRoutes": {"RIPE": []}})

    data = {"overlaps": [overlap_info]}

    await display.display_overlaps(data, "AS12345")


@pytest.mark.asyncio
async def test_sort_and_group_panels() -> None:
    """Test panel sorting and grouping."""
    display = IrrDisplay()

    prefix_infos = [
        create_basic_prefix_info(prefix="192.0.2.0/24", categoryOverall="success", rpkiRoutes=[]),
        create_basic_prefix_info(prefix="192.0.2.0/25", categoryOverall="warning", rpkiRoutes=[]),
    ]

    panels = await display.sort_and_group_panels(prefix_infos)
    assert len(panels) > 0


@pytest.mark.asyncio
async def test_fetch_asn_info_error() -> None:
    """Test ASN info fetch error handling."""
    explorer = IrrExplorer()
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_get.side_effect = httpx.RequestError("Connection error")
        with pytest.raises(httpx.RequestError):
            await explorer.fetch_asn_info("AS12345")
    await explorer.close()


@pytest.mark.asyncio
async def test_display_direct_origins_with_errors() -> None:
    """Test direct origins display with error conditions."""
    display = IrrDisplay()

    error_prefix = COMMON_PREFIX_INFO.copy()
    error_prefix.update(
        {
            "categoryOverall": "error",
            "rpkiRoutes": [],
            "bgpOrigins": [],
            "messages": [{"category": "error", "text": "Test error"}],
            "goodnessOverall": 0,
        }
    )

    data = {"directOrigin": [error_prefix]}

    await display.display_direct_origins(data, "AS12345")


@pytest.mark.asyncio
async def test_display_all_overlaps_error() -> None:
    """Test all overlaps display with error handling."""
    display = IrrDisplay()
    with patch("irrexplorer_cli.irrexplorer.IrrExplorer.fetch_prefix_info") as mock_fetch:
        mock_fetch.side_effect = httpx.HTTPError("Test error")
        await display.display_all_overlaps("192.0.2.0/24")


@pytest.mark.asyncio
async def test_fetch_asn_info_with_backoff() -> None:
    """Test ASN info fetch with backoff retry."""
    explorer = IrrExplorer()
    mock_request = httpx.Request("GET", "https://irrexplorer.nlnog.net/api/prefixes/asn/AS12345")
    mock_response = httpx.Response(200, json={}, request=mock_request)

    with patch("httpx.AsyncClient.get") as mock_get:
        mock_get.side_effect = [
            httpx.RequestError("Timeout"),  # First attempt fails
            mock_response,  # Second attempt succeeds
        ]
        result = await explorer.fetch_asn_info("AS12345")
        assert isinstance(result, dict)
    await explorer.close()


@pytest.mark.asyncio
async def test_display_prefix_info_with_overlaps() -> None:
    """Test prefix info display with overlapping prefixes."""
    display = IrrDisplay()
    test_data = [
        create_basic_prefix_info(prefix="192.0.2.0/16", categoryOverall="info", rpkiRoutes=[]),
        create_basic_prefix_info(prefix="192.0.2.0/24", categoryOverall="danger", rpkiRoutes=[]),
    ]
    await display.display_prefix_info(test_data)


def test_get_rpki_status() -> None:
    """Test RPKI status extraction from prefix info."""
    display = IrrDisplay()

    # Test with RPKI routes present
    prefix_with_routes = {"rpkiRoutes": [{"rpkiStatus": "VALID"}]}

    # Test with RPKI routes present
    prefix_with_routes = {"rpkiRoutes": [{"rpkiStatus": "VALID"}]}
    assert display.get_rpki_status(prefix_with_routes) == "VALID"

    # Test with no RPKI routes
    prefix_without_routes: dict[str, list[Any]] = {"rpkiRoutes": []}
    assert display.get_rpki_status(prefix_without_routes) == "UNKNOWN"

    # Test with missing rpkiRoutes key
    prefix_missing_routes: dict[str, Any] = {}
    assert display.get_rpki_status(prefix_missing_routes) == "UNKNOWN"
