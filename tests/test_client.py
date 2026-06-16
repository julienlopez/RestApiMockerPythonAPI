import json

import pytest
import responses

from rest_api_mocker import MockRequestError, RestApiMocker


@responses.activate
def test_add_mock_posts_expected_payload():
    responses.add(
        responses.POST,
        "http://localhost:8080/internal/mock",
        status=200,
    )

    mocker = RestApiMocker("http://localhost", 8080)
    mocker.add_mock(
        method="GET",
        path_pattern="/users/.*",
        status=200,
        body={"id": 1, "name": "Ada"},
    )

    assert len(responses.calls) == 1
    sent = json.loads(responses.calls[0].request.body)
    assert sent == {
        "method": "GET",
        "path_pattern": "/users/.*",
        "status": 200,
        "body": json.dumps({"id": 1, "name": "Ada"}),
        "conditions": [],
    }


@responses.activate
def test_add_mock_raises_on_non_200():
    responses.add(
        responses.POST,
        "http://localhost:8080/internal/mock",
        status=500,
        body="boom",
    )

    mocker = RestApiMocker("http://localhost", 8080)
    with pytest.raises(MockRequestError) as exc_info:
        mocker.add_mock("GET", "/x", 200, {})

    assert exc_info.value.status_code == 500
    assert exc_info.value.response_text == "boom"


def test_base_url_strips_trailing_slash():
    mocker = RestApiMocker("http://localhost/", 8080)
    assert mocker.base_url == "http://localhost:8080"


@responses.activate
def test_conditions_default_is_not_shared():
    responses.add(
        responses.POST, "http://localhost:8080/internal/mock", status=200
    )
    mocker = RestApiMocker("http://localhost", 8080)

    mocker.add_mock("GET", "/a", 200, {})
    mocker.add_mock("GET", "/b", 200, {})

    first = json.loads(responses.calls[0].request.body)["conditions"]
    second = json.loads(responses.calls[1].request.body)["conditions"]
    assert first == [] and second == []
