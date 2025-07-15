import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile
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

@pytest.mark.django_db
def test_happy_path_upload():
    """Test successful file upload with all required fields."""
    user = User.objects.create_user(email="test@example.com", password="test123")
    client = APIClient()
    client.force_authenticate(user=user)

    file_content = b"This is a test file content"
    uploaded_file = SimpleUploadedFile("test.txt", file_content, content_type="text/plain")
    
    response = client.post(
        reverse("api:fileversion-list"),
        {"file": uploaded_file, "file_name": "test_document.txt"},
        format="multipart"
    )
    
    assert response.status_code == 201
    assert response.data["version_number"] == 1
    assert response.data["file_obj"]["name"] == "test_document.txt"
    assert "content_hash" in response.data
    assert len(response.data["content_hash"]) == 64

@pytest.mark.django_db
def test_duplicate_content_upload():
    """Test that uploading the same content creates new versions with same content_hash."""
    user = User.objects.create_user(email="test@example.com", password="test123")
    client = APIClient()
    client.force_authenticate(user=user)

    file_content = b"Same content for both uploads"
    
    uploaded_file1 = SimpleUploadedFile("first.txt", file_content, content_type="text/plain")
    response1 = client.post(
        reverse("api:fileversion-list"),
        {"file": uploaded_file1, "file_name": "first_document.txt"},
        format="multipart"
    )
    assert response1.status_code == 201
    first_version_id = response1.data["id"]
    first_content_hash = response1.data["content_hash"]

    uploaded_file2 = SimpleUploadedFile("second.txt", file_content, content_type="text/plain")
    response2 = client.post(
        reverse("api:fileversion-list"),
        {"file": uploaded_file2, "file_name": "second_document.txt"},
        format="multipart"
    )
    assert response2.status_code == 201
    second_version_id = response2.data["id"]
    second_content_hash = response2.data["content_hash"]

    assert first_version_id != second_version_id
    assert first_content_hash == second_content_hash

@pytest.mark.django_db
def test_large_file_upload():
    """Test upload of a large file (simulated with 1MB content)."""
    user = User.objects.create_user(email="test@example.com", password="test123")
    client = APIClient()
    client.force_authenticate(user=user)

    large_content = b"x" * (1024 * 1024)
    uploaded_file = SimpleUploadedFile("large.txt", large_content, content_type="text/plain")
    
    response = client.post(
        reverse("api:fileversion-list"),
        {"file": uploaded_file, "file_name": "large_document.txt"},
        format="multipart"
    )
    
    assert response.status_code == 201
    assert response.data["version_number"] == 1
    assert "content_hash" in response.data

@pytest.mark.django_db
def test_different_file_types():
    """Test upload of different file types."""
    user = User.objects.create_user(email="test@example.com", password="test123")
    client = APIClient()
    client.force_authenticate(user=user)

    pdf_content = b"%PDF-1.4\nTest PDF content"
    pdf_file = SimpleUploadedFile("test.pdf", pdf_content, content_type="application/pdf")
    response = client.post(
        reverse("api:fileversion-list"),
        {"file": pdf_file, "file_name": "test_document.pdf"},
        format="multipart"
    )
    assert response.status_code == 201

    image_content = b"fake image content"
    image_file = SimpleUploadedFile("test.jpg", image_content, content_type="image/jpeg")
    response = client.post(
        reverse("api:fileversion-list"),
        {"file": image_file, "file_name": "test_image.jpg"},
        format="multipart"
    )
    assert response.status_code == 201

@pytest.mark.django_db
def test_missing_file_field():
    """Test upload without file field."""
    user = User.objects.create_user(email="test@example.com", password="test123")
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(
        reverse("api:fileversion-list"),
        {"file_name": "test_document.txt"},
        format="multipart"
    )
    
    assert response.status_code in [400, 500]

@pytest.mark.django_db
def test_missing_file_name():
    """Test upload without file_name field."""
    user = User.objects.create_user(email="test@example.com", password="test123")
    client = APIClient()
    client.force_authenticate(user=user)

    uploaded_file = SimpleUploadedFile("test.txt", b"content", content_type="text/plain")
    response = client.post(
        reverse("api:fileversion-list"),
        {"file": uploaded_file},
        format="multipart"
    )
    
    assert response.status_code in [400, 500]

@pytest.mark.django_db
def test_empty_file_upload():
    """Test upload of an empty file (should be forbidden)."""
    user = User.objects.create_user(email="test@example.com", password="test123")
    client = APIClient()
    client.force_authenticate(user=user)

    uploaded_file = SimpleUploadedFile("empty.txt", b"", content_type="text/plain")
    response = client.post(
        reverse("api:fileversion-list"),
        {"file": uploaded_file, "file_name": "empty_document.txt"},
        format="multipart"
    )
    
    assert response.status_code == 400
    assert "file" in response.data
    assert "empty" in str(response.data["file"]).lower()

@pytest.mark.django_db
def test_same_filename_different_content():
    """Test that same filename with different content creates new version."""
    user = User.objects.create_user(email="test@example.com", password="test123")
    client = APIClient()
    client.force_authenticate(user=user)

    uploaded_file1 = SimpleUploadedFile("test.txt", b"First content", content_type="text/plain")
    response1 = client.post(
        reverse("api:fileversion-list"),
        {"file": uploaded_file1, "file_name": "test_document.txt"},
        format="multipart"
    )
    assert response1.status_code == 201
    first_version = response1.data["version_number"]

    uploaded_file2 = SimpleUploadedFile("test.txt", b"Second content", content_type="text/plain")
    response2 = client.post(
        reverse("api:fileversion-list"),
        {"file": uploaded_file2, "file_name": "test_document.txt"},
        format="multipart"
    )
    assert response2.status_code == 201
    second_version = response2.data["version_number"]

    assert second_version == first_version + 1
    assert response1.data["content_hash"] != response2.data["content_hash"]

@pytest.mark.django_db
def test_multiple_users_same_content():
    """Test that different users can upload same content and get different versions."""
    user1 = User.objects.create_user(email="user1@example.com", password="test123")
    user2 = User.objects.create_user(email="user2@example.com", password="test123")
    client = APIClient()

    file_content = b"Same content for both users"
    
    client.force_authenticate(user=user1)
    uploaded_file1 = SimpleUploadedFile("test.txt", file_content, content_type="text/plain")
    response1 = client.post(
        reverse("api:fileversion-list"),
        {"file": uploaded_file1, "file_name": "test_document.txt"},
        format="multipart"
    )
    assert response1.status_code == 201

    client.force_authenticate(user=user2)
    uploaded_file2 = SimpleUploadedFile("test.txt", file_content, content_type="text/plain")
    response2 = client.post(
        reverse("api:fileversion-list"),
        {"file": uploaded_file2, "file_name": "test_document.txt"},
        format="multipart"
    )
    assert response2.status_code == 201

    assert response1.data["id"] != response2.data["id"]
    assert response1.data["content_hash"] == response2.data["content_hash"]
