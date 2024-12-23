"""Data models for IRR Explorer API responses."""

import logging
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, model_validator

logger = logging.getLogger(__name__)


class BaseRoute(BaseModel):
    """Base model for route information."""

    rpkiStatus: str
    rpkiMaxLength: Optional[int]
    asn: int
    rpslText: str
    rpslPk: str


class RpkiRoute(BaseRoute):
    """RPKI route information model."""


class IrrRoute(BaseRoute):
    """IRR route information model."""


class Message(BaseModel):
    """Message model for API responses."""

    text: str
    category: str


class PrefixInfo(BaseModel):
    """Prefix information model containing route and status details."""

    prefix: str
    rir: str
    bgpOrigins: List[int]
    rpkiRoutes: List[RpkiRoute]
    irrRoutes: Dict[str, List[IrrRoute]]
    categoryOverall: str
    messages: List[Message]
    prefixSortKey: str
    goodnessOverall: int

    def __init__(self, **data: Any) -> None:
        logger.debug("Initializing PrefixInfo with data: %s", data)
        super().__init__(**data)
        logger.debug("PrefixInfo initialized successfully for prefix: %s", self.prefix)

    @model_validator(mode="after")
    def validate_prefix_info(self) -> "PrefixInfo":
        """Validate the prefix information after model creation."""
        logger.debug("Validating PrefixInfo for prefix: %s", self.prefix)
        logger.debug(
            "Category: %s, RIR: %s, BGP Origins count: %d", self.categoryOverall, self.rir, len(self.bgpOrigins)
        )
        return self


class AsResponse(BaseModel):
    """Response model for AS queries."""

    directOrigin: List[PrefixInfo]
    overlaps: List[PrefixInfo]


class PrefixResult(BaseModel):
    """Prefix query result information."""

    prefix: str
    categoryOverall: str
    rir: str
    rpkiRoutes: List[RpkiRoute]
    bgpOrigins: List[int]
    irrRoutes: Dict[str, List[IrrRoute]]
    messages: List[Message]


class AsSets(BaseModel):
    """AS Sets information."""

    setsPerIrr: Dict[str, List[str]]


class AsnResult(BaseModel):
    """ASN query result information."""

    directOrigin: List[PrefixResult]
    overlaps: List[PrefixResult]
