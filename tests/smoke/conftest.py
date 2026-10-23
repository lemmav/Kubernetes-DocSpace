"""Shared fixtures for DocSpace smoke tests.

Environment:
    BASE_URL   portal address reachable from the runner (default http://localhost:8092)
    NAMESPACE  Kubernetes namespace DocSpace is installed in (default "default")
"""
import json
import os
import subprocess

import pytest
import requests

REQUEST_TIMEOUT = 30  # seconds


class Portal:
    """Thin wrapper around requests that prefixes every path with BASE_URL."""

    def __init__(self, base_url):
        self.base_url = base_url.rstrip("/")
        self._session = requests.Session()

    def get(self, path, **kwargs):
        return self._session.get(self.base_url + path, timeout=REQUEST_TIMEOUT, **kwargs)

    def post(self, path, **kwargs):
        return self._session.post(self.base_url + path, timeout=REQUEST_TIMEOUT, **kwargs)


@pytest.fixture(scope="session")
def portal():
    """Anonymous client for the portal behind the router."""
    return Portal(os.environ.get("BASE_URL", "http://localhost:8092"))


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
