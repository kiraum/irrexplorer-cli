""" Fixtures for tests """

from typing import Any

from irrexplorer_cli.models import PrefixInfo

COMMON_SETS_DATA = {"setsPerIrr": {"RIPE": ["AS-TEST"], "ARIN": ["AS-TEST2"]}}
COMMON_RPKI_ROUTE = {
    "rpkiStatus": "VALID",
    "rpkiMaxLength": 24,
    "asn": 12345,
    "rpslText": "route: 192.0.2.0/24",
    "rpslPk": "192.0.2.0/24AS12345/ML24",
}

COMMON_PREFIX_INFO = {
    "prefix": "192.0.2.0/24",
    "categoryOverall": "success",
    "rir": "RIPE",
    "rpkiRoutes": [COMMON_RPKI_ROUTE],
    "bgpOrigins": [12345],
    "irrRoutes": {},
    "messages": [],
    "prefixSortKey": "1",
    "goodnessOverall": 1,
}

COMMON_ASN_DATA = {
    "directOrigin": [COMMON_PREFIX_INFO],
    "overlaps": [],
}

COMMON_SETS_DATA = {
    "setsPerIrr": {
        "RIPE": ["AS-TEST1", "AS-TEST2"],
        "ARIN": ["AS-TEST3"],
        "AFRINIC": ["AS-TEST4", "AS-TEST5", "AS-TEST6"],
    }
}


def create_basic_prefix_info(**kwargs: Any) -> PrefixInfo:
    """Create a basic PrefixInfo object."""
    data = COMMON_PREFIX_INFO.copy()
    data.update(kwargs)
    return PrefixInfo.model_validate(data)
