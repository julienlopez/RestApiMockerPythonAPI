"""Dataclasses mirroring the RestApiMocker server's JSON types."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List


@dataclass
class ServerConfig:
    """Server configuration, as returned by ``GET /internal/config``."""

    public_port: int
    private_port: int

    @classmethod
    def from_dict(cls, data: dict) -> "ServerConfig":
        return cls(
            public_port=data["public_port"],
            private_port=data["private_port"],
        )


@dataclass
class RequestRecord:
    """A single request recorded by the public server.

    Returned by ``GET /internal/history``.
    """

    method: str
    path: str
    timestamp: int

    @classmethod
    def from_dict(cls, data: dict) -> "RequestRecord":
        return cls(
            method=data["method"],
            path=data["path"],
            timestamp=data["timestamp"],
        )


@dataclass
class MockConfig:
    """A configured mock response.

    Returned by ``GET /internal/mocks``. Note that ``body`` is the JSON string
    the server stores, not a decoded object.
    """

    method: str
    path_pattern: str
    status: int
    body: str
    conditions: List[Any] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> "MockConfig":
        return cls(
            method=data["method"],
            path_pattern=data["path_pattern"],
            status=data["status"],
            body=data.get("body", ""),
            conditions=list(data.get("conditions") or []),
        )
