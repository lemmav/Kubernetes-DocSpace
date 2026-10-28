"""Shared fixtures for DocSpace smoke tests.

Environment:
    BASE_URL          portal address reachable from the runner (default http://localhost:8092)
    NAMESPACE         Kubernetes namespace DocSpace is installed in (default "default")
    PORTAL_EMAIL      owner email created by the first-run wizard (default smoke@smoke.com)
    PORTAL_PASSWORD   owner password (default Smoke-Test-2026)
    LICENSE_FILE      path to license.lic (the wizard of DocSpace Enterprise requires a license)
    LICENSE           license content, used when LICENSE_FILE is not set
"""
import hashlib
import json
import os
import subprocess

import pytest
import requests

REQUEST_TIMEOUT = 30  # seconds

PORTAL_EMAIL = os.environ.get("PORTAL_EMAIL", "smoke@smoke.com")
PORTAL_PASSWORD = os.environ.get("PORTAL_PASSWORD", "Smoke-Test-2026")


class Portal:
    """Thin wrapper around requests that prefixes every path with BASE_URL.

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


def password_hash(settings, password=PORTAL_PASSWORD):
    """Hash the password the way the portal expects (PBKDF2-SHA256, params from settings)."""
    params = settings["passwordHash"]
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode(), params["salt"].encode(),
        params["iterations"], params["size"] // 8,
    ).hex()


def read_license():
    """License bytes from LICENSE_FILE or LICENSE; None when neither is set."""
    path = os.environ.get("LICENSE_FILE")
    if path and os.path.isfile(path):
        with open(path, "rb") as license_file:
            return license_file.read()
    content = os.environ.get("LICENSE")
    return content.encode() if content else None


def body_of(response):
    """The `response` payload of a portal API reply; the raw text goes into the error if absent."""
    data = response.json()
    assert "response" in data, f"unexpected API reply: {response.text[:300]}"
    return data["response"]


def base_url():
    return os.environ.get("BASE_URL", "http://localhost:8092")


@pytest.fixture
def portal():
    """Anonymous client for the portal behind the router.

    Created per test: the wizard and login set auth cookies, which must not
    leak into tests that check anonymous access.
    """
    return Portal(base_url())


@pytest.fixture(scope="session")
def settings():
    """Anonymous portal settings as they were before any test touched the portal."""
    response = Portal(base_url()).get("/api/2.0/settings")
    assert response.status_code == 200, response.text[:300]
    return body_of(response)


@pytest.fixture(scope="session")
def wizard_completed(settings):
    """Run the first-run wizard once so the portal owner exists.

    The wizard token is present in the settings only while the wizard is pending,
    so an already initialized portal is left as it is.
    """
    portal = Portal(base_url())
    token = settings.get("wizardToken")
    if not token:
        return False
    confirm = {"confirm": token}

    required = portal.get("/api/2.0/settings/license/required", headers=confirm)
    if required.status_code == 200 and required.json().get("response"):
        license_bytes = read_license()
        assert license_bytes, "a license is required: set LICENSE_FILE (path) or LICENSE (content)"
        uploaded = portal.post(
            "/api/2.0/settings/license", headers=confirm,
            files={"Files": ("license.lic", license_bytes)},
        )
        assert uploaded.status_code == 200, f"license upload failed: {uploaded.text[:300]}"

    response = portal.put(
        "/api/2.0/settings/wizard/complete", headers=confirm,
        json={
            "email": PORTAL_EMAIL,
            "PasswordHash": password_hash(settings),
            "lng": "en",
            "timeZone": "UTC",
        },
    )
    assert response.status_code == 200, f"wizard failed: {response.text[:300]}"
    assert body_of(response).get("completed"), f"wizard not completed: {response.text[:300]}"
    return True


@pytest.fixture(scope="session")
def admin(settings, wizard_completed):
    """Client authorized as the portal owner."""
    portal = Portal(base_url())
    response = portal.post(
        "/api/2.0/authentication",
        json={"userName": PORTAL_EMAIL, "passwordHash": password_hash(settings)},
    )
    assert response.status_code == 200, f"login failed: {response.text[:300]}"
    token = body_of(response).get("token")
    assert token, f"no token in login reply: {response.text[:300]}"
    return portal.with_token(token)


@pytest.fixture(scope="session")
def namespace():
    return os.environ.get("NAMESPACE", "default")


@pytest.fixture(scope="session")
def pods(namespace):
    """All pods of the namespace as parsed `kubectl get pods -o json` items."""
    result = subprocess.run(
        ["kubectl", "get", "pods", "-n", namespace, "-o", "json"],
        capture_output=True, text=True, check=True,
    )
    return json.loads(result.stdout)["items"]
