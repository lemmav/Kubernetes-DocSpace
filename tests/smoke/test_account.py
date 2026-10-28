"""First-run wizard and owner authentication."""
import pytest

from conftest import PORTAL_EMAIL, body_of, password_hash

pytestmark = pytest.mark.portal


def test_wizard_creates_the_portal_owner(wizard_completed, portal):
    # After the wizard the anonymous settings no longer expose a wizard token.
    settings = body_of(portal.get("/api/2.0/settings"))

    assert "wizardToken" not in settings, "wizard is still pending"


def test_owner_can_log_in(admin):
    assert admin.token


def test_login_with_wrong_password_is_rejected(portal, settings, wizard_completed):
    response = portal.post(
        "/api/2.0/authentication",
        json={"userName": PORTAL_EMAIL, "passwordHash": password_hash(settings, "wrong-password")},
    )

    assert response.status_code != 200, "wrong password must not authenticate"
    assert "token" not in response.text


def test_people_self_returns_the_owner(admin):
    response = admin.get("/api/2.0/people/@self")

    assert response.status_code == 200, response.text[:300]
    assert body_of(response)["email"] == PORTAL_EMAIL


def test_private_data_requires_authorization(portal, wizard_completed):
    response = portal.get("/api/2.0/people/@self")

    assert response.status_code in (401, 403), response.text[:300]
