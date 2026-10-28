"""Files and rooms: creation and a storage round-trip (needs the owner session)."""
import uuid

import pytest

from conftest import body_of

pytestmark = pytest.mark.portal

CUSTOM_ROOM = 5  # roomType of a custom room


def test_my_documents_folder_is_available(admin):
    response = admin.get("/api/2.0/files/@my")

    assert response.status_code == 200, response.text[:300]
    assert body_of(response)["current"]["id"]


def test_empty_document_can_be_created(admin):
    # Needs Document Server to build the document from a template.
    response = admin.post("/api/2.0/files/@my/file", json={"title": "smoke.docx"})

    assert response.status_code == 200, response.text[:300]
    created = body_of(response)
    assert created["id"]
    assert created["webUrl"]


def test_folder_can_be_created(admin):
    parent_id = body_of(admin.get("/api/2.0/files/@my"))["current"]["id"]

    response = admin.post(f"/api/2.0/files/folder/{parent_id}", json={"title": "smoke folder"})

    assert response.status_code == 200, response.text[:300]
    assert body_of(response)["id"]


def test_custom_room_can_be_created(admin):
    response = admin.post("/api/2.0/files/rooms", json={"title": "smoke room", "roomType": CUSTOM_ROOM})

    assert response.status_code == 200, response.text[:300]
    assert body_of(response)["id"]


def test_uploaded_file_downloads_back_unchanged(admin):
    content = f"smoke upload {uuid.uuid4().hex}".encode()

    upload = admin.post("/api/2.0/files/@my/upload", files={"file": ("smoke-upload.txt", content)})
    assert upload.status_code == 200, upload.text[:300]
    uploaded = body_of(upload)[0]

    download = admin.get(uploaded["viewUrl"])
    assert download.status_code == 200, download.text[:300]
    assert download.content == content


@pytest.mark.parametrize("source, target, signature", [
    ("smoke-convert.docx", "smoke-converted.pdf", b"%PDF"),
])
def test_document_server_converts_files(admin, source, target, signature):
    # End-to-end proof that DocSpace, Document Server, Redis and RabbitMQ work together.
    created = admin.post("/api/2.0/files/@my/file", json={"title": source})
    assert created.status_code == 200, created.text[:300]
    source_id = body_of(created)["id"]
    my_folder = body_of(admin.get("/api/2.0/files/@my"))["current"]["id"]

    converted = admin.post(
        f"/api/2.0/files/file/{source_id}/copyas",
        json={"destFolderId": my_folder, "destTitle": target},
        timeout=180,
    )
    assert converted.status_code == 200, converted.text[:300]

    file_info = admin.get(f"/api/2.0/files/file/{body_of(converted)['id']}")
    content = admin.get(body_of(file_info)["viewUrl"])
    assert content.content.startswith(signature), content.content[:8]
