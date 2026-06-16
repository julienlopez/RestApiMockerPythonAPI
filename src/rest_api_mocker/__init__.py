"""rest_api_mocker — a small Python wrapper for RestApiMocker."""

from __future__ import annotations

from .client import RestApiMocker
from .exceptions import MockRequestError, RestApiMockerError
from .models import MockConfig, RequestRecord, ServerConfig

__all__ = [
    "RestApiMocker",
    "RestApiMockerError",
    "MockRequestError",
    "ServerConfig",
    "RequestRecord",
    "MockConfig",
]
__version__ = "0.1.0"
