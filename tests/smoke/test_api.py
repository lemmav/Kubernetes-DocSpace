"""Public (unauthenticated) API endpoints answer with valid JSON."""
import pytest

pytestmark = pytest.mark.portal


def test_capabilities_endpoint_returns_json_object(portal):
    response = portal.get("/api/2.0/capabilities.json")

    assert response.status_code == 200, response.text[:300]
    assert isinstance(response.json(), dict)


def test_build_version_is_reported(portal):
    # Anonymous endpoint backed by the database, so it proves api + MySQL work.
    response = portal.get("/api/2.0/settings/version/build")

    assert response.status_code == 200, response.text[:300]
    assert response.json().get("response"), f"version info is empty: {response.text[:300]}"


def test_portal_identifies_itself_as_docspace(portal):
    # `docSpace` and `version` are part of the anonymous settings response.
    response = portal.get("/api/2.0/settings")

    assert response.status_code == 200, response.text[:300]
    settings = response.json()["response"]
    assert settings.get("docSpace"), f"portal does not identify as DocSpace: {settings}"
    assert settings.get("version"), f"portal version is missing: {settings}"
