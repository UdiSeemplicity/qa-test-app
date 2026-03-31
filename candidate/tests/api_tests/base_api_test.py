from __future__ import annotations

import requests

from tests.clients.dashboard.findings_api import FindingsApi
from tests.clients.dashboard.health_api import DashboardHealthApi
from tests.clients.dashboard.stats_api import StatsApi
from tests.clients.dashboard.vulnerabilities_api import VulnerabilitiesApi
from tests.clients.scanner.assets_api import AssetsApi
from tests.clients.scanner.health_api import ScannerHealthApi
from tests.clients.scanner.scans_api import ScansApi

DASHBOARD_BASE_URL = "http://localhost:8000"
SCANNER_BASE_URL = "http://localhost:8001"


def build_api_clients(session: requests.Session) -> dict:
    return {
        "findings_api": FindingsApi(f"{DASHBOARD_BASE_URL}/findings", session=session),
        "stats_api": StatsApi(f"{DASHBOARD_BASE_URL}/stats", session=session),
        "vulnerabilities_api": VulnerabilitiesApi(f"{DASHBOARD_BASE_URL}/vulnerabilities", session=session),
        "dashboard_health_api": DashboardHealthApi(f"{DASHBOARD_BASE_URL}/health", session=session),
        "assets_api": AssetsApi(f"{SCANNER_BASE_URL}/assets", session=session),
        "scans_api": ScansApi(f"{SCANNER_BASE_URL}/scans", session=session),
        "scanner_health_api": ScannerHealthApi(f"{SCANNER_BASE_URL}/health", session=session),
    }


class BaseApiTest:
    @classmethod
    def setup_class(cls) -> None:
        cls.session = requests.Session()
        clients = build_api_clients(cls.session)

        cls.findings_api = clients["findings_api"]
        cls.stats_api = clients["stats_api"]
        cls.vulnerabilities_api = clients["vulnerabilities_api"]
        cls.dashboard_health_api = clients["dashboard_health_api"]
        cls.assets_api = clients["assets_api"]
        cls.scans_api = clients["scans_api"]
        cls.scanner_health_api = clients["scanner_health_api"]

    @classmethod
    def teardown_class(cls) -> None:
        cls.session.close()
