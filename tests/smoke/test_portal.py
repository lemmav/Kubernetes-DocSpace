"""The portal is reachable through the router and routes requests correctly."""
import pytest

pytestmark = pytest.mark.portal


def test_root_page_is_served(portal):
    response = portal.get("/")

    assert response.status_code == 200
    assert "<html" in response.text.lower(), "root page should return HTML"


@pytest.mark.parametrize("path", ["/login/health", "/doceditor/health"])
def test_frontend_service_is_healthy(portal, path):
    response = portal.get(path)

    assert response.status_code == 200


def test_unknown_api_path_returns_404_not_gateway_error(portal):
    # 502/503 here would mean the router lost its upstream.
    response = portal.get("/api/2.0/this-endpoint-does-not-exist")

    assert response.status_code == 404
