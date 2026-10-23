"""Public (unauthenticated) API endpoints answer with valid JSON."""
import pytest

pytestmark = pytest.mark.portal


def test_capabilities_endpoint_returns_json_object(portal):
    response = portal.get("/api/2.0/capabilities.json")

    assert response.status_code == 200
    assert isinstance(response.json(), dict)


def test_build_version_is_reported(portal):
    # Needs api + database, so it also proves the backend is wired up.
    response = portal.get("/api/2.0/settings/version/build")

    assert response.status_code == 200
    assert response.json().get("response"), "version info should not be empty"


def test_common_portal_settings_are_available(portal):
    response = portal.get("/api/2.0/settings")

    assert response.status_code == 200
    assert response.json().get("response"), "settings should not be empty"
