"""Values the tests compare against: titles, signatures, status codes and JSON field names."""
HTTP_OK = 200
HTTP_NOT_FOUND = 404
HTTP_REJECTED = (401, 403)  # anonymous access to private data

WIZARD_LANGUAGE = "en"
WIZARD_TIME_ZONE = "UTC"
LICENSE_FILE_NAME = "license.lic"

HTML_MARKER = "<html"


class RoomType:
    CUSTOM = 5


class Field:
    """Keys of the JSON the portal API returns."""
    RESPONSE = "response"
    ID = "id"
    TITLE = "title"
    EMAIL = "email"
    TOKEN = "token"
    WIZARD_TOKEN = "wizardToken"
    COMPLETED = "completed"
    DOC_SPACE = "docSpace"
    VERSION = "version"
    VIEW_URL = "viewUrl"
    WEB_URL = "webUrl"
    CURRENT = "current"


class Title:
    DOCUMENT = "smoke.docx"
    FOLDER = "smoke folder"
    ROOM = "smoke room"
    UPLOAD = "smoke-upload.txt"
    VERSIONED = "smoke-versions.txt"
    CONVERSION_SOURCE = "smoke-convert.docx"
    CONVERSION_TARGET = "smoke-converted.pdf"


class Signature:
    """First bytes of a file format."""
    PDF = b"%PDF"
