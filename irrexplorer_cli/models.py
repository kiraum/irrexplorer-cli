"""Data models for IRR Explorer API responses."""

from typing import Dict, List, Optional

from pydantic import BaseModel


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
