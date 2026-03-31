from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

import requests

from tests.api_tests.base_api_test import build_api_clients
from tests.integration_tests.base_integration_test import BaseIntegrationTest


class TestConcurrentScanImports(BaseIntegrationTest):
    def test_concurrent_scan_imports_create_multiple_scan_records_and_findings(
        self,
        created_asset,
        seed_vulnerability,
    ):
        vulnerability_ids = [seed_vulnerability["id"]]
        initial_count = self.db_client.count_findings_for_asset_and_vulnerabilities(
            created_asset["id"],
            vulnerability_ids,
        )

        def run_scan() -> dict:
            session = requests.Session()
            try:
                clients = build_api_clients(session)
                return clients["scans_api"].create_scan(
                    {
                        "asset_id": created_asset["id"],
                        "scanner_name": "ConcurrentScanner",
                        "vulnerability_ids": vulnerability_ids,
                    }
                )
            finally:
                session.close()

        with ThreadPoolExecutor(max_workers=2) as executor:
            responses = list(executor.map(lambda _: run_scan(), range(2)))

        final_count = self.db_client.count_findings_for_asset_and_vulnerabilities(
            created_asset["id"],
            vulnerability_ids,
        )
        created_findings = self.db_client.get_findings_for_asset_and_vulnerabilities(
            created_asset["id"],
            vulnerability_ids,
        )

        assert len(responses) == 2
        assert all(response["status"] == "completed" for response in responses)
        assert final_count >= initial_count + 2
        assert len([row for row in created_findings if row["scanner"] == "ConcurrentScanner"]) >= 2
