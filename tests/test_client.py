import json

import pytest
import responses

from rest_api_mocker import (
    MockConfig,
    MockRequestError,
    RequestRecord,
    RestApiMocker,
    ServerConfig,
)

BASE = "http://localhost:8080/internal"


def make_mocker():
    return RestApiMocker("http://localhost", 8080)


@responses.activate
def test_add_mock_posts_expected_payload():
    responses.add(responses.POST, f"{BASE}/mock", status=200)

    make_mocker().add_mock(
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
    responses.add(responses.POST, f"{BASE}/mock", status=500, body="boom")

    with pytest.raises(MockRequestError) as exc_info:
        make_mocker().add_mock("GET", "/x", 200, {})

    assert exc_info.value.status_code == 500
    assert exc_info.value.response_text == "boom"


def test_base_url_strips_trailing_slash():
    mocker = RestApiMocker("http://localhost/", 8080)
    assert mocker.base_url == "http://localhost:8080"


@responses.activate
def test_conditions_default_is_not_shared():
    responses.add(responses.POST, f"{BASE}/mock", status=200)
    mocker = make_mocker()

    mocker.add_mock("GET", "/a", 200, {})
    mocker.add_mock("GET", "/b", 200, {})

    first = json.loads(responses.calls[0].request.body)["conditions"]
    second = json.loads(responses.calls[1].request.body)["conditions"]
    assert first == [] and second == []


@responses.activate
def test_get_config():
    responses.add(
        responses.GET,
        f"{BASE}/config",
        json={"public_port": 9090, "private_port": 80},
        status=200,
    )

    config = make_mocker().get_config()
    assert config == ServerConfig(public_port=9090, private_port=80)


@responses.activate
def test_get_history():
    responses.add(
        responses.GET,
        f"{BASE}/history",
        json=[{"method": "GET", "path": "/users/1", "timestamp": 1700000000}],
        status=200,
    )

    history = make_mocker().get_history()
    assert history == [
        RequestRecord(method="GET", path="/users/1", timestamp=1700000000)
    ]


@responses.activate
def test_get_mocks():
    responses.add(
        responses.GET,
        f"{BASE}/mocks",
        json=[
            {
                "method": "GET",
                "path_pattern": "/users/.*",
                "status": 200,
                "body": "{}",
                "conditions": [],
            }
        ],
        status=200,
    )

    mocks = make_mocker().get_mocks()
    assert mocks == [
        MockConfig(
            method="GET",
            path_pattern="/users/.*",
            status=200,
            body="{}",
            conditions=[],
        )
    ]


@responses.activate
def test_delete_mock_by_index():
    responses.add(
        responses.DELETE, f"{BASE}/mock/0", status=200, body="Mock deleted"
    )

    make_mocker().delete_mock(0)
    assert responses.calls[0].request.url == f"{BASE}/mock/0"


@responses.activate
def test_delete_mock_out_of_range_raises():
    responses.add(
        responses.DELETE, f"{BASE}/mock/99", status=404, body="out of range"
    )

    with pytest.raises(MockRequestError) as exc_info:
        make_mocker().delete_mock(99)
    assert exc_info.value.status_code == 404


@responses.activate
def test_delete_all_mocks():
    responses.add(
        responses.DELETE, f"{BASE}/mocks", status=200, body="All mocks deleted"
    )

    make_mocker().delete_all_mocks()
    assert len(responses.calls) == 1


@responses.activate
def test_delete_mocks_by_pattern():
    responses.add(
        responses.DELETE,
        f"{BASE}/mocks/by-pattern",
        status=200,
        body="1 mock(s) deleted",
    )

    make_mocker().delete_mocks_by_pattern("/users/:id")

    assert responses.calls[0].request.params == {"path_pattern": "/users/:id"}


@responses.activate
def test_delete_mocks_by_pattern_no_match_raises():
    responses.add(
        responses.DELETE,
        f"{BASE}/mocks/by-pattern",
        status=404,
        body="No mocks found",
    )

    with pytest.raises(MockRequestError):
        make_mocker().delete_mocks_by_pattern("/nope")
