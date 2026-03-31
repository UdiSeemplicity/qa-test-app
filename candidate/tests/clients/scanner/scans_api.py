from __future__ import annotations

from typing import Any

from candidate.tests.clients.base_api import BaseApi


class ScansApi(BaseApi):
    def list_scans(
        self,
        *,
        page: int | None = None,
        per_page: int | None = None,
        asset_id: int | None = None,
        is_negative: bool = False,
    ):
        params = {
            "page": page,
            "per_page": per_page,
            "asset_id": asset_id,
        }
        return self.get(
            "",
            params={k: v for k, v in params.items() if v is not None},
            is_negative=is_negative,
        )

    def get_scan(
        self,
        scan_id: int,
        *,
        is_negative: bool = False,
    ):
        return self.get(f"/{scan_id}", is_negative=is_negative)

    def create_scan(
        self,
        payload: dict[str, Any],
        *,
        is_negative: bool = False,
    ):
        return self.post("", json=payload, is_negative=is_negative)
