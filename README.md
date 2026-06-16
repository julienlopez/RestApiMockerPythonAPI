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
