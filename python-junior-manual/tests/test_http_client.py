"""No live network requests are made in this test suite."""
import io
from unittest.mock import patch
from urllib.error import HTTPError, URLError

import pytest

from exercises.http_client import APIClientError, APIHTTPError, get_json


class FakeResponse:
    def __init__(self, data: bytes, status: int = 200):
        self.data = data
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self, count):
        return self.data[:count]


def error(status):
    return HTTPError("https://example.com/api", status, "error", {}, io.BytesIO(b""))


def test_success_and_timeout_argument():
    with patch("exercises.http_client.urlopen", return_value=FakeResponse(b'{"ok":true}')) as call:
        assert get_json("https://example.com/api", timeout=2) == {"ok": True}
    assert call.call_args.kwargs["timeout"] == 2


def test_retry_then_success():
    delays = []
    with patch("exercises.http_client.urlopen", side_effect=[error(503), error(429), FakeResponse(b"[1,2]")]) as call:
        assert get_json("https://example.com/api", retries=2, backoff=0.5, sleep=delays.append) == [1, 2]
    assert call.call_count == 3
    assert delays == [0.5, 1.0]


def test_400_does_not_retry():
    with patch("exercises.http_client.urlopen", side_effect=error(400)) as call:
        with pytest.raises(APIHTTPError) as ex:
            get_json("https://example.com/api", retries=3, sleep=lambda _: None)
    assert ex.value.status == 400
    assert call.call_count == 1


def test_500_retry_limit():
    with patch("exercises.http_client.urlopen", side_effect=error(500)) as call:
        with pytest.raises(APIHTTPError) as ex:
            get_json("https://example.com/api", retries=2, sleep=lambda _: None)
    assert ex.value.status == 500
    assert call.call_count == 3


def test_network_error_retry_and_exhaustion():
    with patch("exercises.http_client.urlopen", side_effect=URLError("offline")) as call:
        with pytest.raises(APIClientError, match="network failure"):
            get_json("https://example.com/api", retries=1, sleep=lambda _: None)
    assert call.call_count == 2


def test_bad_json():
    with patch("exercises.http_client.urlopen", return_value=FakeResponse(b"not-json")):
        with pytest.raises(APIClientError, match="invalid JSON"):
            get_json("https://example.com/api")


def test_bad_utf8():
    with patch("exercises.http_client.urlopen", return_value=FakeResponse(b"\xff")):
        with pytest.raises(APIClientError, match="invalid JSON"):
            get_json("https://example.com/api")


def test_too_large_response():
    with patch("exercises.http_client.urlopen", return_value=FakeResponse(b"a" * 2_000_001)):
        with pytest.raises(APIClientError, match="exceeds"):
            get_json("https://example.com/api")


@pytest.mark.parametrize("url", ["http://example.com", "file:///etc/passwd", "https://user:pass@example.com", "https://", "example.com"])
def test_invalid_url(url):
    with pytest.raises(ValueError):
        get_json(url)


@pytest.mark.parametrize("kwargs", [{"timeout": 0}, {"retries": -1}, {"retries": 11}, {"backoff": -1}])
def test_invalid_arguments(kwargs):
    with pytest.raises(ValueError):
        get_json("https://example.com", **kwargs)


def test_non_success_response_status():
    with patch("exercises.http_client.urlopen", return_value=FakeResponse(b"{}", 503)) as call:
        with pytest.raises(APIHTTPError):
            get_json("https://example.com", retries=1, sleep=lambda _: None)
    assert call.call_count == 2
