import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from propylon_document_manager.file_versions.models.user import User
from propylon_document_manager.file_versions.models.file_version import FileVersion
from propylon_document_manager.file_versions.models.file import File

@pytest.mark.django_db
def test_upload_and_versioning(tmp_path):
    user = User.objects.create_user(email="user1@example.com", password="user123")
    client = APIClient()
    client.force_authenticate(user=user)

    file_path = tmp_path / "test.txt"
    file_path.write_text("first version")
    with open(file_path, "rb") as f:
        response = client.post(
            reverse("api:fileversion-list"),
            {"file": f, "file_name": "test_document.txt"},
            format="multipart"
        )
    assert response.status_code == 201
    assert response.data["version_number"] == 1

    file_path.write_text("second version")
    with open(file_path, "rb") as f:
        response2 = client.post(
            reverse("api:fileversion-list"),
            {"file": f, "file_name": "test_document.txt"},
            format="multipart"
        )
    assert response2.status_code == 201
    assert response2.data["version_number"] == 2

    file_obj_id = response.data["file_obj"]["id"]
    file_obj_id2 = response2.data["file_obj"]["id"]
    assert file_obj_id == file_obj_id2

@pytest.mark.django_db
def test_fetch_by_content_hash(tmp_path):
    user = User.objects.create_user(email="user2@example.com", password="user123")
    client = APIClient()
    client.force_authenticate(user=user)

    file_path = tmp_path / "hash_test.txt"
    file_path.write_text("hash test")
    with open(file_path, "rb") as f:
        response = client.post(
            reverse("api:fileversion-list"),
            {"file": f, "file_name": "hash_test.txt"},
            format="multipart"
        )
    assert response.status_code == 201
    content_hash = response.data["content_hash"]

    url = reverse("api:fileversion-by-hash", kwargs={"content_hash": content_hash})
    response2 = client.get(url)
    assert response2.status_code == 200
    assert response2.data["content_hash"] == content_hash

@pytest.mark.django_db
def test_cannot_access_others_files(tmp_path):
    user1 = User.objects.create_user(email="user1@example.com", password="user123")
    user2 = User.objects.create_user(email="user2@example.com", password="user123")
    client = APIClient()
    client.force_authenticate(user=user1)

    file_path = tmp_path / "test.txt"
    file_path.write_text("some content")
    with open(file_path, "rb") as f:
        response = client.post(
            reverse("api:fileversion-list"),
            {"file": f, "file_name": "secret_document.txt"},
            format="multipart"
        )
    fileversion_id = response.data["id"]

    client.force_authenticate(user=user2)
    url = reverse("api:fileversion-detail", kwargs={"id": fileversion_id})
    response2 = client.get(url)
    assert response2.status_code == 404

@pytest.mark.django_db
def test_unauthenticated_access(tmp_path):
    client = APIClient()
    response = client.get(reverse("api:fileversion-list"))
    assert response.status_code == 403

@pytest.mark.django_db
def test_cannot_modify_others_files(tmp_path):
    user1 = User.objects.create_user(email="user1@example.com", password="user123")
    user2 = User.objects.create_user(email="user2@example.com", password="user123")
    client = APIClient()
    client.force_authenticate(user=user1)

    file_path = tmp_path / "test.txt"
    file_path.write_text("some content")
    with open(file_path, "rb") as f:
        response = client.post(
            reverse("api:fileversion-list"),
            {"file": f, "file_name": "secret_document.txt"},
            format="multipart"
        )
    fileversion_id = response.data["id"]

    client.force_authenticate(user=user2)
    url = reverse("api:fileversion-detail", kwargs={"id": fileversion_id})
    response2 = client.delete(url)
    assert response2.status_code == 404

    response3 = client.patch(url, {"file_name": "hacked.txt"})
    assert response3.status_code == 404
