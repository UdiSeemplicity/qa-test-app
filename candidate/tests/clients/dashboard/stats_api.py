from candidate.tests.clients.base_api import BaseApi


class StatsApi(BaseApi):
    def get_risk_score(
        self,
        *,
        is_negative: bool = False,
    ):
        return self.get("/risk-score", is_negative=is_negative)

    def get_summary(
        self,
        *,
        is_negative: bool = False,
    ):
        return self.get("/summary", is_negative=is_negative)
