import io
import os
import pytest
from PIL import Image

def create_fake_image() -> bytes:
    """Helper to create a small valid JPEG byte stream."""
    file = io.BytesIO()
    image = Image.new("RGB", (100, 100), color="red")
    image.save(file, "jpeg")
    file.seek(0)
    return file.read()

def test_upload_and_auth_flow(client):
    # Ensure storage root exists for test
    os.makedirs("/tmp/grabpic_test_storage/uploads", exist_ok=True)
    
    # 1. Upload a mock image
    image_bytes = create_fake_image()
    upload_resp = client.post(
        "/v1/ingest/upload",
        files={"file": ("test_photo.jpg", image_bytes, "image/jpeg")}
    )
    
    assert upload_resp.status_code == 200, upload_resp.text
    data = upload_resp.json()
    assert data["faces_detected"] == 1
    
    # 2. Authenticate with a "selfie" (using the same image structure)
    selfie_resp = client.post(
        "/v1/auth/selfie",
        files={"file": ("selfie.jpg", image_bytes, "image/jpeg")}
    )
    
    assert selfie_resp.status_code == 200, selfie_resp.text
    selfie_data = selfie_resp.json()
    assert "grab_id" in selfie_data
    grab_id = selfie_data["grab_id"]
    
    # 3. Retrieve user's images
    images_resp = client.get(f"/v1/grab/{grab_id}/images")
    assert images_resp.status_code == 200, images_resp.text
    images_data = images_resp.json()
    
    assert "images" in images_data
    assert len(images_data["images"]) == 1
    assert "test_photo.jpg" in images_data["images"][0]["file_path"]

def test_selfie_auth_no_faces(client, monkeypatch):
    # Temporarily make the mock return empty to test no face logic
    from tests.conftest import MockFaceEngine
    
    class EmptyFaceEngine(MockFaceEngine):
        def extract_from_bgr(self, image_bgr):
            return []
            
    from app.deps import configure_face_engine
    configure_face_engine(EmptyFaceEngine())
    
    image_bytes = create_fake_image()
    selfie_resp = client.post(
        "/v1/auth/selfie",
        files={"file": ("selfie.jpg", image_bytes, "image/jpeg")}
    )
    
    assert selfie_resp.status_code == 400
    assert selfie_resp.json()["error"]["code"] == "NO_FACE_FOUND"
    
    # Restore normal mock for other tests
    configure_face_engine(MockFaceEngine())
