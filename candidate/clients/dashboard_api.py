from typing import Any

import requests


class DashboardApiClient:
    FINDINGS_ENDPOINT = "findings"
    VULNERABILITIES_ENDPOINT = "vulnerabilities"
    HEALTH_ENDPOINT = "health"
    STATS_ENDPOINT = "stats"

    DEFAULT_TIMEOUT_SECONDS = 10

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

    def close(self) -> None:
        self.session.close()

    def _url(self, *parts: str | int) -> str:
        suffix = "/".join(str(p).strip("/") for p in parts)
        return f"{self.base_url}/{suffix}" if suffix else self.base_url

    def check_health(self) -> requests.Response:
        return self.session.get(
            url=self._url(self.HEALTH_ENDPOINT),
            timeout=self.DEFAULT_TIMEOUT_SECONDS,
        )

    def create_finding(self, payload: dict[str, Any]) -> requests.Response:
        return self.session.post(
            url=self._url(self.FINDINGS_ENDPOINT),
            json=payload,
            timeout=self.DEFAULT_TIMEOUT_SECONDS,
        )

    def get_finding(self, finding_id: int) -> requests.Response:
        return self.session.get(
            url=self._url(self.FINDINGS_ENDPOINT, finding_id),
            timeout=self.DEFAULT_TIMEOUT_SECONDS,
        )

    def update_finding_status(
        self,
        finding_id: int,
        status: str,
        notes: str | None = None,
    ) -> requests.Response:
        body: dict[str, Any] = {"status": status}
        if notes is not None:
            body["notes"] = notes
        return self.session.put(
            url=self._url(self.FINDINGS_ENDPOINT, finding_id, "status"),
            json=body,
            timeout=self.DEFAULT_TIMEOUT_SECONDS,
        )

    def update_status(self, finding_id: int, status: str, notes: str | None = None) -> requests.Response:
        return self.update_finding_status(finding_id, status=status, notes=notes)

    def dismiss_finding(self, finding_id: int) -> requests.Response:
        return self.session.delete(
            url=self._url(self.FINDINGS_ENDPOINT, finding_id),
            timeout=self.DEFAULT_TIMEOUT_SECONDS,
        )

    def list_findings(self, params: dict[str, Any] | None = None) -> requests.Response:
        return self.session.get(
            url=self._url(self.FINDINGS_ENDPOINT),
            params=params,
            timeout=self.DEFAULT_TIMEOUT_SECONDS,
        )

    def search_findings(self, query: str) -> requests.Response:
        return self.session.get(
            url=self._url(self.FINDINGS_ENDPOINT, "search"),
            params={"q": query},
            timeout=self.DEFAULT_TIMEOUT_SECONDS,
        )

    def list_vulnerabilities(self, params: dict[str, Any] | None = None) -> requests.Response:
        return self.session.get(
            url=self._url(self.VULNERABILITIES_ENDPOINT),
            params=params,
            timeout=self.DEFAULT_TIMEOUT_SECONDS,
        )

    def get_vulnerability(self, vuln_id: int) -> requests.Response:
        return self.session.get(
            url=self._url(self.VULNERABILITIES_ENDPOINT, vuln_id),
            timeout=self.DEFAULT_TIMEOUT_SECONDS,
        )

    def get_stats_summary(self) -> requests.Response:
        return self.session.get(
            url=self._url(self.STATS_ENDPOINT, "summary"),
            timeout=self.DEFAULT_TIMEOUT_SECONDS,
        )

    def get_risk_score(self) -> requests.Response:
        return self.session.get(
            url=self._url(self.STATS_ENDPOINT, "risk-score"),
            timeout=self.DEFAULT_TIMEOUT_SECONDS,
        )
