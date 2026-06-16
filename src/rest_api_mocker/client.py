"""Client for talking to a RestApiMocker server."""

from __future__ import annotations

import json
from typing import Any, Optional, Sequence

import requests

from .exceptions import MockRequestError

DEFAULT_TIMEOUT = 30.0


class RestApiMocker:
    """A thin wrapper around the RestApiMocker HTTP control API.

    Example:
        >>> mocker = RestApiMocker("http://localhost", 8080)
        >>> mocker.add_mock(
        ...     method="GET",
        ...     path_pattern="/users/.*",
        ...     status=200,
        ...     body={"id": 1, "name": "Ada"},
        ... )
    """

    def __init__(
        self,
        url: str,
        port: int,
        *,
        timeout: float = DEFAULT_TIMEOUT,
        session: Optional[requests.Session] = None,
    ) -> None:
        """Create a client.

        Args:
            url: Base URL of the mocker server, e.g. ``"http://localhost"``.
            port: Port the mocker server listens on.
            timeout: Per-request timeout in seconds.
            session: Optional pre-configured :class:`requests.Session`. When
                omitted, a new session is created and owned by this instance.
        """
        self.url = url.rstrip("/")
        self.port = port
        self.timeout = timeout
        self._session = session or requests.Session()
        self._owns_session = session is None

    @property
    def base_url(self) -> str:
        """The fully-qualified base URL, including port."""
        return f"{self.url}:{self.port}"

    def add_mock(
        self,
        method: str,
        path_pattern: str,
        status: int,
        body: Any,
        conditions: Optional[Sequence[dict]] = None,
    ) -> None:
        """Register a mock response on the server.

        Args:
            method: HTTP method to match, e.g. ``"GET"``.
            path_pattern: Path (or pattern) the mock should match.
            status: HTTP status code the mock should return.
            body: Response body. Serialized to a JSON string before sending.
            conditions: Optional list of matching conditions.

        Raises:
            MockRequestError: If the server returns a non-200 response.
        """
        mock_definition = {
            "method": method,
            "path_pattern": path_pattern,
            "status": status,
            "body": json.dumps(body),
            "conditions": list(conditions) if conditions is not None else [],
        }
        response = self._session.post(
            f"{self.base_url}/internal/mock",
            json=mock_definition,
            timeout=self.timeout,
        )
        if response.status_code != 200:
            raise MockRequestError(response.status_code, response.text)

    def close(self) -> None:
        """Close the underlying session, if this instance owns it."""
        if self._owns_session:
            self._session.close()

    def __enter__(self) -> "RestApiMocker":
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()
