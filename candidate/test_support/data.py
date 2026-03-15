from typing import Any

DEFAULT_SCANNER = "Nessus"


def build_finding_payload(asset_id: int, vulnerability_id: int, *, notes: str) -> dict[str, Any]:
    return {
        "asset_id": asset_id,
        "vulnerability_id": vulnerability_id,
        "scanner": DEFAULT_SCANNER,
        "notes": notes,
    }


def build_scan_payload(
    asset_id: int,
    vulnerability_ids: list[int],
    *,
    scanner_name: str = DEFAULT_SCANNER,
) -> dict[str, Any]:
    return {
        "asset_id": asset_id,
        "scanner_name": scanner_name,
        "vulnerability_ids": vulnerability_ids,
    }
