"""Test suite for data models."""

from typing import Dict, List

from irrexplorer_cli.models import AsResponse, AsSets, IrrRoute, PrefixInfo
from tests.fixtures import COMMON_PREFIX_INFO, COMMON_RPKI_ROUTE


def test_prefix_info_model() -> None:
    """Test PrefixInfo model validation and instantiation."""
    data = COMMON_PREFIX_INFO.copy()
    data.update(
        {
            "rir": "RIPE NCC",
            "bgpOrigins": [202196],
            "categoryOverall": "warning",
            "messages": [{"category": "warning", "text": "Test message"}],
        }
    )

    prefix_info = PrefixInfo.model_validate(data)
    assert prefix_info.prefix == "192.0.2.0/24"  # Updated to match fixture
    assert prefix_info.rir == "RIPE NCC"
    assert prefix_info.bgpOrigins == [202196]
    assert prefix_info.categoryOverall == "warning"
    assert len(prefix_info.rpkiRoutes) == 1
    assert len(prefix_info.messages) == 1
    assert prefix_info.irrRoutes == {}


def test_irr_route_model() -> None:
    """Test IrrRoute model validation."""
    irr_route = IrrRoute.model_validate(COMMON_RPKI_ROUTE)
    assert irr_route.rpkiStatus == "VALID"
    assert irr_route.asn == 12345


def test_as_response_model() -> None:
    """Test AsResponse model validation."""
    data: Dict[str, List[PrefixInfo]] = {"directOrigin": [], "overlaps": []}
    response = AsResponse.model_validate(data)
    assert isinstance(response.directOrigin, list)
    assert isinstance(response.overlaps, list)


def test_as_sets_model() -> None:
    """Test AsSets model validation."""
    data: Dict[str, Dict[str, List[str]]] = {"setsPerIrr": {"RIPE": ["AS-TEST"]}}
    sets = AsSets.model_validate(data)
    assert "RIPE" in sets.setsPerIrr
