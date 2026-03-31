from __future__ import annotations

import os
import time
import uuid

import pytest
import requests
from playwright.sync_api import Page, sync_playwright

from candidate.tests.api_tests.base_api_test import build_api_clients
from candidate.tests.db_client import DB_CONFIG, DbClient


@pytest.fixture(scope="session")
def http_session() -> requests.Session:
    return requests.Session()


@pytest.fixture()
def page() -> Page:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=os.getenv("HEADLESS", "true").lower() == "true",
        )
        context = browser.new_context(viewport={"width": 1600, "height": 900})
        page = context.new_page()

        yield page

        context.close()
        browser.close()


@pytest.fixture(scope="session")
def db_client() -> DbClient:
    client = DbClient(**DB_CONFIG)
    yield client
    client.close()


@pytest.fixture(scope="session")
def api_clients(http_session: requests.Session) -> dict:
    return build_api_clients(http_session)


@pytest.fixture(scope="session")
def seed_vulnerability(api_clients: dict) -> dict:
    vulnerabilities = api_clients["vulnerabilities_api"].list_vulnerabilities()
    assert vulnerabilities, "Expected seeded vulnerabilities to exist"
    return vulnerabilities[0]


@pytest.fixture(scope="session")
def seed_asset(api_clients: dict) -> dict:
    assets_page = api_clients["assets_api"].list_assets(per_page=50)
    assert assets_page["items"], "Expected seeded active assets to exist"
    return assets_page["items"][0]


@pytest.fixture()
def unique_suffix() -> str:
    return f"{int(time.time() * 1000)}-{uuid.uuid4().hex[:6]}"


@pytest.fixture()
def created_asset(api_clients: dict, unique_suffix: str) -> dict:
    payload = {
        "hostname": f"qa-auto-{unique_suffix}",
        "ip_address": f"10.10.{int(time.time()) % 250}.{int(time.time() * 1000) % 250}",
        "asset_type": "server",
        "environment": "staging",
        "os": "Ubuntu 22.04",
    }
    return api_clients["assets_api"].create_asset(payload)


@pytest.fixture()
def created_finding(
    api_clients: dict,
    created_asset: dict,
    seed_vulnerability: dict,
    unique_suffix: str,
) -> dict:
    payload = {
        "asset_id": created_asset["id"],
        "vulnerability_id": seed_vulnerability["id"],
        "scanner": "pytest",
        "notes": f"created by api test {unique_suffix}",
    }
    return api_clients["findings_api"].create_finding(payload)
