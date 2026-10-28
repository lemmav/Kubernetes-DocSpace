"""The portal is reachable through the router and routes requests correctly."""
import pytest

pytestmark = pytest.mark.portal


def test_root_page_is_served(portal):
    response = portal.get("/")

    assert response.status_code == 200, response.text[:300]
    assert "<html" in response.text.lower(), "root page should return HTML"


def test_healthchecks_service_is_alive(portal):
    # Exposed by the router (healthchecks.enabled=true in the chart by default).
    response = portal.get("/healthchecks/liveness/")

    assert response.status_code == 200, response.text[:300]


def test_unknown_api_path_returns_404_not_gateway_error(portal):
    # 502/503 here would mean the router lost its upstream.
    response = portal.get("/api/2.0/this-endpoint-does-not-exist")

    assert response.status_code == 404, response.text[:300]
