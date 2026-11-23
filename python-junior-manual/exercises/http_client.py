"""A resilient JSON GET client using the Python standard library.

The requester should only access HTTPS endpoints from trusted application code.
Retry is limited to transient network failures or selected server errors.
"""

import json
import logging
import time
from collections.abc import Callable
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

logger = logging.getLogger(__name__)
RETRYABLE_STATUSES = frozenset({429, 500, 502, 503, 504})


class APIClientError(Exception):
    """A request failed or returned an invalid response."""


class APIHTTPError(APIClientError):
    """The server returned an HTTP error status."""

    def __init__(self, status: int, message: str):
        self.status = status
        super().__init__(message)


def get_json(
    url: str,
    *,
    timeout: float = 5.0,
    retries: int = 2,
    backoff: float = 0.25,
    sleep: Callable[[float], None] = time.sleep,
) -> Any:
    """Fetch JSON via HTTPS, retrying transient GET failures."""
    parsed = urlsplit(url)
    if parsed.scheme.lower() != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("url must be an HTTPS URL without embedded credentials")
    if timeout <= 0 or retries < 0 or backoff < 0:
        raise ValueError("timeout must be positive, retries/backoff nonnegative")
    if retries > 10:
        raise ValueError("retries must not exceed 10")

    request = Request(url, headers={"Accept": "application/json", "User-Agent": "python-junior-manual/1.0"})
    for attempt in range(retries + 1):
        try:
            with urlopen(request, timeout=timeout) as response:
                if not 200 <= response.status < 300:
                    raise APIHTTPError(response.status, f"HTTP {response.status}")
                raw = response.read(2_000_001)
                if len(raw) > 2_000_000:
                    raise APIClientError("response exceeds 2 MB limit")
                try:
                    return json.loads(raw.decode("utf-8-sig"))
                except (UnicodeError, json.JSONDecodeError) as exc:
                    raise APIClientError("invalid JSON response") from exc
        except HTTPError as exc:
            error = APIHTTPError(exc.code, f"HTTP {exc.code}")
            retryable = exc.code in RETRYABLE_STATUSES
        except APIHTTPError as exc:
            error = exc
            retryable = exc.status in RETRYABLE_STATUSES
        except (URLError, TimeoutError, OSError) as exc:
            error = APIClientError(f"network failure: {type(exc).__name__}")
            retryable = True

        if not retryable or attempt == retries:
            raise error
        delay = min(backoff * (2 ** attempt), 8.0)
        logger.warning("HTTP request failed; retrying (attempt %s/%s)", attempt + 1, retries + 1)
        sleep(delay)

    raise AssertionError("unreachable")
