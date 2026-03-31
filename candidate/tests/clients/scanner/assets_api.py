from __future__ import annotations

from typing import Any

from candidate.tests.clients.base_api import BaseApi


class AssetsApi(BaseApi):
    def list_assets(
        self,
        *,
        page: int | None = None,
        per_page: int | None = None,
        environment: str | None = None,
        asset_type: str | None = None,
        is_negative: bool = False,
    ):
        params = {
            "page": page,
            "per_page": per_page,
            "environment": environment,
            "asset_type": asset_type,
        }
        return self.get(
            "",
            params={k: v for k, v in params.items() if v is not None},
            is_negative=is_negative,
        )

    def get_asset(
        self,
        asset_id: int,
        *,
        is_negative: bool = False,
    ):
        return self.get(f"/{asset_id}", is_negative=is_negative)

    def create_asset(
        self,
        payload: dict[str, Any],
        *,
        is_negative: bool = False,
    ):
        return self.post("", json=payload, is_negative=is_negative)

    def update_asset(
        self,
        asset_id: int,
        payload: dict[str, Any],
        *,
        is_negative: bool = False,
    ):
        return self.put(f"/{asset_id}", json=payload, is_negative=is_negative)

    def deactivate_asset(
        self,
        asset_id: int,
        *,
        is_negative: bool = False,
    ):
        return self.delete(f"/{asset_id}", is_negative=is_negative)
