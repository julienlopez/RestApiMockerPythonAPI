# rest-api-mocker

A small Python wrapper for [RestApiMocker](https://github.com/julienlopez/RestApiMockerPythonAPI).

## Installation

```bash
pip install rest-api-mocker
```

Until it's published, install from a checkout:

```bash
pip install -e ".[test]"
```

## Usage

```python
from rest_api_mocker import RestApiMocker

mocker = RestApiMocker("http://localhost", 8080)
mocker.add_mock(
    method="GET",
    path_pattern="/users/.*",
    status=200,
    body={"id": 1, "name": "Ada"},
)
```

`RestApiMocker` can also be used as a context manager so the underlying HTTP
session is closed for you:

```python
with RestApiMocker("http://localhost", 8080) as mocker:
    mocker.add_mock("GET", "/health", 200, {"ok": True})
```

### API

The client mirrors the server's `/internal` control plane:

| Method | Description |
| --- | --- |
| `add_mock(method, path_pattern, status, body, conditions=None)` | Register a mock response. |
| `get_mocks() -> list[MockConfig]` | List all configured mocks. |
| `delete_mock(index)` | Delete a mock by its 0-based index. |
| `delete_all_mocks()` | Delete every configured mock. |
| `delete_mocks_by_pattern(path_pattern)` | Delete all mocks matching a path pattern. |
| `get_config() -> ServerConfig` | Get the server's public/private ports. |
| `get_history() -> list[RequestRecord]` | Get the recorded request history. |

```python
mocker.add_mock("GET", "/users/.*", 200, {"id": 1})

config = mocker.get_config()          # ServerConfig(public_port=9090, private_port=80)
mocks = mocker.get_mocks()            # [MockConfig(...)]
history = mocker.get_history()        # [RequestRecord(method=..., path=..., timestamp=...)]

mocker.delete_mocks_by_pattern("/users/.*")
mocker.delete_all_mocks()
```

The `MockConfig`, `ServerConfig` and `RequestRecord` dataclasses are importable
from the top-level package.

### Errors

A non-success response from the mocker server raises `MockRequestError`
(a subclass of `RestApiMockerError`):

```python
from rest_api_mocker import MockRequestError

try:
    mocker.add_mock("GET", "/x", 200, {})
except MockRequestError as exc:
    print(exc.status_code, exc.response_text)
```

## Development

```bash
pip install -e ".[test]"
pytest
```
