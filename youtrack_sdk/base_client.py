from typing import Any
from typing import Final
from typing import Optional
from typing import final
from urllib.parse import urlencode

import httpx

from youtrack_sdk.types import TimeoutSpec


class BaseClient:
    def __init__(
        self,
        *,
        base_url: str,
        timeout: Optional[int | float | TimeoutSpec] = None,
    ) -> None:
        """
        :param base_url: YouTrack instance URL (e.g. https://example.com/youtrack)
        :param timeout: (optional) How long to wait for the server to send data before giving up,
            as a float or int, or timeout spec
        """
        self._base_url: Final = base_url
        self._timeout: Final = timeout

    @final
    def get_absolute_url(self, *, path: str) -> str:
        return f"{self._base_url}{path}"

    @final
    def _build_url(
        self,
        *,
        path: str,
        fields: Optional[str] = None,
        offset: Optional[int] = None,
        count: Optional[int] = None,
        **kwargs: Any,  # noqa: ANN401
    ) -> str:
        query: Final = urlencode(
            {
                key: str(value).lower() if isinstance(value, bool) else value
                for key, value in {
                    "fields": fields,
                    "$skip": offset,
                    "$top": count,
                    **kwargs,
                }.items()
                if value is not None
            },
            doseq=True,
        )
        return f"{self._base_url}/api{path}?{query}"

    @staticmethod
    def _to_httpx_timeout(timeout: Optional[int | float | TimeoutSpec]) -> Optional[httpx.Timeout | float]:
        httpx_timeout: Optional[httpx.Timeout | float]
        match timeout:
            case None | float():
                httpx_timeout = timeout
            case int():
                httpx_timeout = float(timeout)
            case TimeoutSpec():
                httpx_timeout = httpx.Timeout(
                    connect=timeout.connect_timeout,
                    read=timeout.read_timeout,
                )
        return httpx_timeout

    @staticmethod
    def _get_headers(token: str) -> dict[str, str]:
        return {"Authorization": f"Bearer {token}"}
