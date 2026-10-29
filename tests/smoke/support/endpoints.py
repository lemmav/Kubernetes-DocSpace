"""Portal URL paths, so tests never spell them out."""
ROOT = "/"
HEALTH_LIVENESS = "/healthchecks/liveness/"
UNKNOWN_API = "/api/2.0/this-endpoint-does-not-exist"

CAPABILITIES = "/api/2.0/capabilities.json"
BUILD_VERSION = "/api/2.0/settings/version/build"
SETTINGS = "/api/2.0/settings"
LICENSE_REQUIRED = "/api/2.0/settings/license/required"
LICENSE_UPLOAD = "/api/2.0/settings/license"
WIZARD_COMPLETE = "/api/2.0/settings/wizard/complete"

AUTHENTICATION = "/api/2.0/authentication"
PEOPLE_SELF = "/api/2.0/people/@self"

MY_FOLDER = "/api/2.0/files/@my"
MY_FILE = "/api/2.0/files/@my/file"
MY_UPLOAD = "/api/2.0/files/@my/upload"
ROOMS = "/api/2.0/files/rooms"


def folder(parent_id):
    return f"/api/2.0/files/folder/{parent_id}"


def file_info(file_id):
    return f"/api/2.0/files/file/{file_id}"


def file_copy_as(file_id):
    return f"/api/2.0/files/file/{file_id}/copyas"


def file_history(file_id):
    return f"/api/2.0/files/file/{file_id}/history"


def file_update(file_id):
    return f"/api/2.0/files/{file_id}/update"
