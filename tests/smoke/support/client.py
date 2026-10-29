"""HTTP client for the portal API."""
import requests

from support.config import REQUEST_TIMEOUT
from support.constants import HTTP_OK, Field

ERROR_PREVIEW = 300  # characters of a reply shown in an assertion message


class Portal:
    """Thin wrapper around requests that prefixes every path with the portal address.

    Pass `token` to get an authorized client (the API expects it in the
    Authorization header).
    """

    def __init__(self, base_url, token=None):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self._session = requests.Session()
        if token:
            self._session.headers["Authorization"] = token

    def request(self, method, path, **kwargs):
        kwargs.setdefault("timeout", REQUEST_TIMEOUT)
        # The API returns absolute links (e.g. viewUrl); pass them through as they are.
        url = path if path.startswith(("http://", "https://")) else self.base_url + path
        return self._session.request(method, url, **kwargs)

    def get(self, path, **kwargs):
        return self.request("GET", path, **kwargs)

    def post(self, path, **kwargs):
        return self.request("POST", path, **kwargs)

    def put(self, path, **kwargs):
        return self.request("PUT", path, **kwargs)

    def with_token(self, token):
        return Portal(self.base_url, token)


def preview(response):
    """Beginning of a reply for an assertion message."""
    return response.text[:ERROR_PREVIEW]


def body_of(response):
    """The `response` payload of a portal API reply; the raw text goes into the error if absent."""
    data = response.json()
    assert Field.RESPONSE in data, f"unexpected API reply: {preview(response)}"
    return data[Field.RESPONSE]


def expect_ok(response, action):
    """Assert the call succeeded and return its payload."""
    assert response.status_code == HTTP_OK, f"{action} failed: HTTP {response.status_code} {preview(response)}"
    return body_of(response)
