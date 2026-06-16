"""Exceptions raised by :mod:`rest_api_mocker`."""

from __future__ import annotations


class RestApiMockerError(Exception):
    """Base class for all errors raised by this library."""


class MockRequestError(RestApiMockerError):
    """Raised when the mocker server returns a non-success response.

    Attributes:
        status_code: HTTP status code returned by the server.
        response_text: Raw response body returned by the server.
    """

    def __init__(self, status_code: int, response_text: str) -> None:
        self.status_code = status_code
        self.response_text = response_text
        super().__init__(f"Mocker server returned {status_code}: {response_text}")
