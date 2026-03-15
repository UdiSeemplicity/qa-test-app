from typing import Any

import requests


class ScannerApiClient:
    ASSETS_ENDPOINT = "assets"
    SCANS_ENDPOINT = "scans"
    HEALTH_ENDPOINT = "health"

    DEFAULT_TIMEOUT_SECONDS = 10
    SCAN_TIMEOUT_SECONDS = 20

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

    def list_assets(self, *, params: dict[str, Any] | None = None) -> requests.Response:
        return self.session.get(
            url=self._url(self.ASSETS_ENDPOINT),
            params=params,
            timeout=self.DEFAULT_TIMEOUT_SECONDS,
        )

    def create_asset(self, payload: dict[str, Any]) -> requests.Response:
        return self.session.post(
            url=self._url(self.ASSETS_ENDPOINT),
            json=payload,
            timeout=self.DEFAULT_TIMEOUT_SECONDS,
        )

    def get_asset(self, asset_id: int) -> requests.Response:
        return self.session.get(
            url=self._url(self.ASSETS_ENDPOINT, asset_id),
            timeout=self.DEFAULT_TIMEOUT_SECONDS,
        )

    def update_asset(self, asset_id: int, payload: dict[str, Any]) -> requests.Response:
        return self.session.put(
            url=self._url(self.ASSETS_ENDPOINT, asset_id),
            json=payload,
            timeout=self.DEFAULT_TIMEOUT_SECONDS,
        )

    def deactivate_asset(self, asset_id: int) -> requests.Response:
        return self.session.delete(
            url=self._url(self.ASSETS_ENDPOINT, asset_id),
            timeout=self.DEFAULT_TIMEOUT_SECONDS,
        )

    def list_scans(self, *, params: dict[str, Any] | None = None) -> requests.Response:
        return self.session.get(
            url=self._url(self.SCANS_ENDPOINT),
            params=params,
            timeout=self.DEFAULT_TIMEOUT_SECONDS,
        )

    def run_scan(self, payload: dict[str, Any]) -> requests.Response:
        return self.session.post(
            url=self._url(self.SCANS_ENDPOINT),
            json=payload,
            timeout=self.SCAN_TIMEOUT_SECONDS,
        )

    def get_scan(self, scan_id: int) -> requests.Response:
        return self.session.get(
            url=self._url(self.SCANS_ENDPOINT, scan_id),
            timeout=self.DEFAULT_TIMEOUT_SECONDS,
        )
