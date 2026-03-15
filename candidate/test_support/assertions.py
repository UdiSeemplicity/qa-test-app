from typing import Any


def assert_status_code(resp, expected: tuple[int, ...]):
    assert resp.status_code in expected, resp.text


def assert_is_dict(data):
    assert isinstance(data, dict), f"Expected dict response, got: {type(data)}"


def assert_finding_base(data: dict[str, Any]) -> None:
    assert_is_dict(data)
    assert "id" in data
    assert "asset_id" in data
    assert "vulnerability_id" in data
    assert "status" in data


def assert_finding_matches(data: dict[str, Any], *, asset_id: int, vulnerability_id: int) -> None:
    assert data.get("asset_id") == asset_id
    assert data.get("vulnerability_id") == vulnerability_id


def assert_finding_status(data: dict[str, Any], expected_status: str) -> None:
    assert data.get("status") == expected_status
