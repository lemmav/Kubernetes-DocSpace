"""Fixtures of the DocSpace smoke tests; helpers live in the `support` package."""
import pytest

from support import cluster, endpoints
from support.auth import complete_wizard, owner_token
from support.client import Portal, expect_ok
from support.config import BASE_URL, NAMESPACE


def pytest_collection_modifyitems(items):
    """Put the first docstring line of every test into the JUnit XML, the run summary shows it as the test name."""
    for item in items:
        lines = (item.function.__doc__ or "").strip().splitlines()
        if lines:
            item.user_properties.append(("description", lines[0].strip()))


@pytest.fixture
def portal():
    """Anonymous client for the portal behind the router.

    Created per test: the wizard and login set auth cookies, which must not
    leak into tests that check anonymous access.
    """
    return Portal(BASE_URL)


@pytest.fixture(scope="session")
def settings():
    """Anonymous portal settings as they were before any test touched the portal."""
    return expect_ok(Portal(BASE_URL).get(endpoints.SETTINGS), "read settings")


@pytest.fixture(scope="session")
def wizard_completed(settings):
    """Run the first-run wizard once so the portal owner exists."""
    return complete_wizard(Portal(BASE_URL), settings)


@pytest.fixture(scope="session")
def admin(settings, wizard_completed):
    """Client authorized as the portal owner."""
    portal = Portal(BASE_URL)
    return portal.with_token(owner_token(portal, settings))


@pytest.fixture(scope="session")
def pods():
    """All pods of the DocSpace namespace."""
    return cluster.fetch_pods(NAMESPACE)
