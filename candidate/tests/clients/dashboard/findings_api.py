from __future__ import annotations

from typing import Any

from candidate.tests.clients.base_api import BaseApi


class FindingsApi(BaseApi):

    def list_findings(
        self,
        *,
        page: int | None = None,
        per_page: int | None = None,
        status: str | None = None,
        severity: str | None = None,
        asset_id: int | None = None,
        is_negative: bool = False,
    ):
        params = {
            "page": page,
            "per_page": per_page,
            "status": status,
            "severity": severity,
            "asset_id": asset_id,
        }
        return self.get(
            "",
            params={k: v for k, v in params.items() if v is not None},
            is_negative=is_negative,
        )

    def get_finding(
        self,
        finding_id: int,
        *,
        is_negative: bool = False,
    ):
        return self.get(f"/{finding_id}", is_negative=is_negative)

    def create_finding(
        self,
        payload: dict[str, Any],
        *,
        is_negative: bool = False,
    ):
        return self.post("", json=payload, is_negative=is_negative)

    def update_status(
        self,
        finding_id: int,
        payload: dict[str, Any],
        *,
        is_negative: bool = False,
    ):
        return self.put(f"/{finding_id}/status", json=payload, is_negative=is_negative)

    def dismiss_finding(
        self,
        finding_id: int,
        *,
        is_negative: bool = False,
    ):
        return self.delete(f"/{finding_id}", is_negative=is_negative)

    def search(
        self,
        query: str,
        *,
        is_negative: bool = False,
    ):
        return self.get("/search", params={"q": query}, is_negative=is_negative)
