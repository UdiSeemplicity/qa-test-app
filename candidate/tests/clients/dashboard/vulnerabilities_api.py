from candidate.tests.clients.base_api import BaseApi


class VulnerabilitiesApi(BaseApi):
    def list_vulnerabilities(
        self,
        *,
        severity: str | None = None,
        is_negative: bool = False,
    ):
        params = {"severity": severity} if severity is not None else None
        return self.get("", params=params, is_negative=is_negative)

    def get_vulnerability(
        self,
        vulnerability_id: int,
        *,
        is_negative: bool = False,
    ):
        return self.get(f"/{vulnerability_id}", is_negative=is_negative)
