import os
import sys
import uuid

import pytest

sys.path.insert(0, os.path.dirname(__file__))

from clients.dashboard_api import DashboardApiClient
from clients.scanner_api import ScannerApiClient
from db.db_client import DbClient
from candidate.test_support.data import build_finding_payload
from candidate.test_support.extract import extract_items


@pytest.fixture(scope="session")
def dashboard_base_url() -> str:
    return os.getenv("DASHBOARD_BASE_URL", "http://localhost:8000")


@pytest.fixture(scope="session")
def scanner_base_url() -> str:
    return os.getenv("SCANNER_BASE_URL", "http://localhost:8001")


@pytest.fixture(scope="session")
def browser_name() -> str:
    return os.getenv("PW_BROWSER", "webkit")


@pytest.fixture(scope="session")
def api_client(dashboard_base_url: str) -> DashboardApiClient:
    client = DashboardApiClient(base_url=dashboard_base_url)
    yield client
    client.close()


@pytest.fixture(scope="session")
def valid_asset_id(api_client: DashboardApiClient) -> int:
    resp = api_client.list_findings(params={"page": 1, "per_page": 1})
    assert resp.status_code == 200, resp.text
    items = extract_items(resp.json())
    assert items, "No findings available to derive a valid asset_id"
    assert "asset_id" in items[0]
    return int(items[0]["asset_id"])


@pytest.fixture(scope="session")
def valid_vulnerability_id(api_client: DashboardApiClient) -> int:
    resp = api_client.list_vulnerabilities(params={"page": 1, "per_page": 1})
    assert resp.status_code == 200, resp.text
    items = extract_items(resp.json())
    assert items, "No vulnerabilities available to derive a valid vulnerability_id"
    assert "id" in items[0]
    return int(items[0]["id"])


@pytest.fixture(scope="session")
def scanner_client(scanner_base_url: str) -> ScannerApiClient:
    client = ScannerApiClient(base_url=scanner_base_url)
    yield client
    client.close()


@pytest.fixture(scope="session")
def db_client() -> DbClient:
    client = DbClient(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5433")),
        database=os.getenv("DB_NAME", "qa_test"),
        user=os.getenv("DB_USER", "qa_user"),
        password=os.getenv("DB_PASSWORD", "qa_password"),
    )
    yield client
    client.close()


@pytest.fixture()
def test_asset(scanner_client: ScannerApiClient) -> dict:
    unique = uuid.uuid4().hex[:8]
    payload = {
        "hostname": f"qa-auto-{unique}",
        "ip_address": f"10.99.0.{int(unique[:2], 16) % 250 + 1}",
        "asset_type": "server",
        "environment": "staging",
        "os": "Ubuntu 22.04",
    }
    resp = scanner_client.create_asset(payload)
    assert resp.status_code in (200, 201), resp.text
    asset = resp.json()

    yield asset

    asset_id = asset.get("id")
    if asset_id is not None:
        scanner_client.deactivate_asset(asset_id)


@pytest.fixture()
def test_finding(api_client: DashboardApiClient, valid_asset_id: int, valid_vulnerability_id: int) -> dict:
    payload = build_finding_payload(
        asset_id=valid_asset_id,
        vulnerability_id=valid_vulnerability_id,
        notes="QA automation test finding",
    )
    resp = api_client.create_finding(payload)
    assert resp.status_code in (200, 201), resp.text
    finding = resp.json()

    yield finding

    finding_id = finding.get("id")
    if finding_id is not None:
        api_client.dismiss_finding(finding_id)
