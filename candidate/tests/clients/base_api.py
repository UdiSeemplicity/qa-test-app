from __future__ import annotations

from typing import Any
from urllib.parse import urljoin

import requests
from requests import Session


class BaseApi:
    SUCCESS_STATUSES = [200, 201, 202, 204, 307]

    def __init__(
        self,
        base_url: str,
        session: Session | None = None,
        timeout: int = 10,
    ) -> None:
        self.base_url = base_url.rstrip("/") + "/"
        self.session = session or requests.Session()
        self.timeout = timeout

    def build_url(self, path: str = "") -> str:
        normalized_path = path.lstrip("/")
        return urljoin(self.base_url, normalized_path)

    def get(
        self,
        path: str = "",
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        is_negative: bool = False,
        **kwargs: Any,
    ) -> Any:
        response = self.session.get(
            self.build_url(path),
            params=params,
            headers=headers,
            timeout=kwargs.pop("timeout", self.timeout),
            **kwargs,
        )
        return self._process_response(response, is_negative=is_negative)

    def post(
        self,
        path: str = "",
        *,
        json: dict[str, Any] | list[Any] | None = None,
        data: Any | None = None,
        headers: dict[str, str] | None = None,
        is_negative: bool = False,
        **kwargs: Any,
    ) -> Any:
        response = self.session.post(
            self.build_url(path),
            json=json,
            data=data,
            headers=headers,
            timeout=kwargs.pop("timeout", self.timeout),
            **kwargs,
        )
        return self._process_response(response, is_negative=is_negative)

    def put(
        self,
        path: str = "",
        *,
        json: dict[str, Any] | list[Any] | None = None,
        data: Any | None = None,
        headers: dict[str, str] | None = None,
        is_negative: bool = False,
        **kwargs: Any,
    ) -> Any:
        response = self.session.put(
            self.build_url(path),
            json=json,
            data=data,
            headers=headers,
            timeout=kwargs.pop("timeout", self.timeout),
            **kwargs,
        )
        return self._process_response(response, is_negative=is_negative)

    def delete(
        self,
        path: str = "",
        *,
        headers: dict[str, str] | None = None,
        is_negative: bool = False,
        **kwargs: Any,
    ) -> Any:
        response = self.session.delete(
            self.build_url(path),
            headers=headers,
            timeout=kwargs.pop("timeout", self.timeout),
            **kwargs,
        )
        return self._process_response(response, is_negative=is_negative)

    def _process_response(self, response: requests.Response, *, is_negative: bool) -> Any:
        if not is_negative:
            assert response.status_code in self.SUCCESS_STATUSES, (
                f"Unexpected status code: {response.status_code}. "
                f"Expected one of: {self.SUCCESS_STATUSES}. "
                f"Response body: {response.text}"
            )

            if response.status_code == 204 or not response.text.strip():
                return None

            try:
                return response.json()
            except ValueError:
                return response.text

        return response.text
