from candidate.tests.clients.base_api import BaseApi


class DashboardHealthApi(BaseApi):
    def get_health(
        self,
        *,
        is_negative: bool = False,
    ):
        return self.get("", is_negative=is_negative)
