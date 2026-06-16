"""Client for talking to a RestApiMocker server."""

from __future__ import annotations

import json
from typing import Any, Sequence

import requests

from .exceptions import MockRequestError
from .models import MockConfig, RequestRecord, ServerConfig

DEFAULT_TIMEOUT = 30.0


class RestApiMocker:
    """A thin wrapper around the RestApiMocker HTTP control API.

    All methods talk to the server's ``/internal`` control plane.

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
        session: requests.Session | None = None,
    ) -> None:
        """Create a client.

        Args:
            url: Base URL of the mocker server, e.g. ``"http://localhost"``.
            port: Port the mocker server's internal API listens on.
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

    # -- low-level helpers ------------------------------------------------

    def _request(self, method: str, path: str, **kwargs: Any) -> requests.Response:
        """Send a request to ``/internal`` and raise on a non-success status.

        Raises:
            MockRequestError: If the server returns a 4xx/5xx response.
        """
        response = self._session.request(
            method,
            f"{self.base_url}/internal{path}",
            timeout=self.timeout,
            **kwargs,
        )
        if not response.ok:
            raise MockRequestError(response.status_code, response.text)
        return response

    # -- mocks ------------------------------------------------------------

    def add_mock(
        self,
        method: str,
        path_pattern: str,
        status: int,
        body: Any,
        conditions: Sequence[dict[str, Any]] | None = None,
    ) -> None:
        """Register a mock response on the server (``POST /internal/mock``).

        Args:
            method: HTTP method to match, e.g. ``"GET"``.
            path_pattern: Path (or pattern) the mock should match.
            status: HTTP status code the mock should return.
            body: Response body. Serialized to a JSON string before sending.
            conditions: Optional list of matching conditions.

        Raises:
            MockRequestError: If the server returns a non-success response.
        """
        mock_definition = {
            "method": method,
            "path_pattern": path_pattern,
            "status": status,
            "body": json.dumps(body),
            "conditions": list(conditions) if conditions is not None else [],
        }
        self._request("POST", "/mock", json=mock_definition)

    def get_mocks(self) -> list[MockConfig]:
        """Return all configured mocks (``GET /internal/mocks``)."""
        response = self._request("GET", "/mocks")
        return [MockConfig.from_dict(item) for item in response.json()]

    def delete_mock(self, index: int) -> None:
        """Delete a mock by its 0-based index (``DELETE /internal/mock/<index>``).

        Raises:
            MockRequestError: If the index is out of range (404) or the request
                otherwise fails.
        """
        self._request("DELETE", f"/mock/{index}")

    def delete_all_mocks(self) -> None:
        """Delete every configured mock (``DELETE /internal/mocks``)."""
        self._request("DELETE", "/mocks")

    def delete_mocks_by_pattern(self, path_pattern: str) -> None:
        """Delete all mocks whose path pattern matches ``path_pattern``.

        Maps to ``DELETE /internal/mocks/by-pattern?path_pattern=...``.

        Raises:
            MockRequestError: If no mock matches the pattern (404) or the
                request otherwise fails.
        """
        self._request(
            "DELETE",
            "/mocks/by-pattern",
            params={"path_pattern": path_pattern},
        )

    # -- introspection ----------------------------------------------------

    def get_config(self) -> ServerConfig:
        """Return the server's port configuration (``GET /internal/config``)."""
        response = self._request("GET", "/config")
        return ServerConfig.from_dict(response.json())

    def get_history(self) -> list[RequestRecord]:
        """Return the recorded request history (``GET /internal/history``)."""
        response = self._request("GET", "/history")
        return [RequestRecord.from_dict(item) for item in response.json()]

    # -- lifecycle --------------------------------------------------------

    def close(self) -> None:
        """Close the underlying session, if this instance owns it."""
        if self._owns_session:
            self._session.close()

    def __enter__(self) -> RestApiMocker:
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()
