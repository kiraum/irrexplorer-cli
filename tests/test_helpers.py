"""Test suite for helper functions."""

from typing import Any, Dict, List

import pytest

from irrexplorer_cli.helpers import (
    find_least_specific_prefix,
    format_as_sets,
    format_direct_origins,
    format_overlapping_prefixes,
    format_prefix_result,
    validate_asn_format,
    validate_prefix_format,
    validate_url_format,
)
from tests.fixtures import (
    COMMON_ASN_DATA,
    COMMON_PREFIX_INFO,
    COMMON_RPKI_ROUTE,
    COMMON_SETS_DATA,
    create_basic_prefix_info,
)


def test_validate_prefix_format() -> None:
    """Test prefix format validation."""
    assert validate_prefix_format("192.0.2.0/24") is True
    assert validate_prefix_format("2001:db8::/32") is True
    assert validate_prefix_format("invalid") is False
    assert validate_prefix_format("256.256.256.256/24") is False


def test_validate_asn_format() -> None:
    """Test ASN format validation."""
    assert validate_asn_format("AS12345") is True
    assert validate_asn_format("12345") is True
    assert validate_asn_format("as12345") is True
    assert validate_asn_format("invalid") is False
    assert validate_asn_format("AS4294967296") is False  # Too large


def test_format_prefix_result() -> None:
    """Test prefix result formatting."""
    prefix_info = create_basic_prefix_info(
        messages=[{"category": "info", "text": "Test message"}], irrRoutes={"RIPE": []}
    )

    result = format_prefix_result(prefix_info, "DIRECT")
    assert isinstance(result, str)
    assert "192.0.2.0/24" in result
    assert "VALID" in result


@pytest.mark.asyncio
async def test_find_least_specific_prefix() -> None:
    """Test finding least specific prefix."""
    overlaps = [
        create_basic_prefix_info(prefix="192.0.2.0/24"),
        create_basic_prefix_info(prefix="192.0.2.0/23"),
        create_basic_prefix_info(prefix="192.0.2.0/25"),
    ]
    result = await find_least_specific_prefix(overlaps)
    assert result == "192.0.2.0/23"


def test_format_as_sets() -> None:
    """Test AS sets formatting."""
    sets_data = {"setsPerIrr": {"RIPE": ["AS-TEST1", "AS-TEST2"]}}
    format_as_sets("AS12345", sets_data)


def test_format_direct_origins_with_empty_results() -> None:
    """Test direct origins formatting with empty results."""
    empty_results: Dict[str, List[Any]] = {"directOrigin": []}
    format_direct_origins("AS12345", empty_results)


def test_format_overlapping_prefixes_with_complex_data() -> None:
    """Test overlapping prefixes with multiple IRR routes."""
    complex_prefix_info = COMMON_PREFIX_INFO.copy()
    complex_prefix_info.update(
        {
            "bgpOrigins": [12345, 67890],
            "irrRoutes": {"RIPE": [COMMON_RPKI_ROUTE]},
            "messages": [
                {"category": "info", "text": "Test message 1"},
                {"category": "warning", "text": "Test message 2"},
            ],
        }
    )

    complex_data = {"overlaps": [complex_prefix_info]}

    format_overlapping_prefixes("AS12345", complex_data)


@pytest.mark.asyncio
async def test_find_least_specific_prefix_empty() -> None:
    """Test finding least specific prefix with empty list."""
    result = await find_least_specific_prefix([])
    assert result is None


def test_format_direct_origins_with_multiple_routes() -> None:
    """Test direct origins formatting with multiple routes."""
    multi_route_prefix = COMMON_PREFIX_INFO.copy()
    multi_route_prefix.update(
        {
            "rpkiRoutes": [],  # Test no RPKI routes case
            "bgpOrigins": [12345, 67890],
            "irrRoutes": {
                "RIPE": [COMMON_RPKI_ROUTE],
                "ARIN": [
                    {
                        "rpkiStatus": "INVALID",
                        "rpkiMaxLength": 24,
                        "asn": 67890,
                        "rpslText": "route: 192.0.2.0/24",
                        "rpslPk": "192.0.2.0/24AS67890/ML24",
                    }
                ],
            },
        }
    )

    test_data = {"directOrigin": [multi_route_prefix]}

    format_direct_origins("AS12345", test_data)


def test_format_as_sets_with_multiple_irrs() -> None:
    """Test AS sets formatting with multiple IRR databases."""
    format_as_sets("AS12345", COMMON_SETS_DATA)


def test_format_as_sets_empty() -> None:
    """Test AS sets formatting with empty data."""
    format_as_sets("AS12345", {"setsPerIrr": {}})
    format_as_sets("AS12345", {})


def test_format_direct_origins_with_rpki_routes() -> None:
    """Test direct origins formatting with RPKI routes."""
    format_direct_origins("AS12345", COMMON_ASN_DATA)


def test_validate_url_format() -> None:
    """Test URL format validation."""
    # Valid URLs
    assert validate_url_format("https://example.com") is True
    assert validate_url_format("http://sub.example.com/path") is True
    assert validate_url_format("https://example.com/path?query=value") is True
    assert validate_url_format("https://api.example.co.uk/v1") is True

    # Invalid URLs
    assert validate_url_format("example.com") is False
    assert validate_url_format("http://invalid") is False
    assert validate_url_format("https://example.com space") is False
    assert validate_url_format("") is False
