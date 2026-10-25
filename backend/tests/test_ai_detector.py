import io
import pytest
from PIL import Image
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def create_in_memory_image(format="JPEG", size=(200, 200), color=(128, 128, 128)):
    img = Image.new("RGB", size, color=color)
    buf = io.BytesIO()
    img.save(buf, format=format)
    buf.seek(0)
    return buf.getvalue()

def test_model_info_endpoint():
    """Verify model-info endpoint reports honest model configuration."""
    response = client.get("/api/model-info")
    assert response.status_code == 200
    data = response.json()
    assert "umm-maybe/AI-image-detector" in data["model_name"]
    assert data["is_available"] is True
    assert data["load_error"] is None
    assert ".jpg" in data["supported_formats"]

def test_detect_valid_jpeg():
    """Test 1: Upload a valid JPEG image."""
    img_bytes = create_in_memory_image(format="JPEG", color=(70, 130, 180))
    files = {"file": ("test_real.jpg", img_bytes, "image/jpeg")}
    response = client.post("/api/detect", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["prediction"] in ["likely_ai_generated", "likely_real_photograph", "uncertain"]
    assert data["display_label"] in ["Likely AI-Generated", "Likely Real Photograph", "Uncertain Result"]
    assert 0.0 <= data["confidence"] <= 1.0
    assert "probabilities" in data
    assert "ai_generated" in data["probabilities"]
    assert "real_photograph" in data["probabilities"]
    assert len(data["limitations"]) > 0

def test_detect_valid_png():
    """Test 2: Upload a valid PNG image."""
    img_bytes = create_in_memory_image(format="PNG", color=(220, 20, 60))
    files = {"file": ("test_graphic.png", img_bytes, "image/png")}
    response = client.post("/api/detect", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert 0.0 <= data["confidence"] <= 1.0

def test_detect_valid_webp():
    """Test 3: Upload a valid WEBP image."""
    img_bytes = create_in_memory_image(format="WEBP", color=(50, 205, 50))
    files = {"file": ("test_photo.webp", img_bytes, "image/webp")}
    response = client.post("/api/detect", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["prediction"] in ["likely_ai_generated", "likely_real_photograph", "uncertain"]

def test_detect_corrupted_file():
    """Test 4: Upload a corrupted file with image extension."""
    corrupted_bytes = b"\xFF\xD8\xFF\xE0\x00\x10JFIF" + b"\x00" * 20 + b"INVALID_GARBAGE_BYTES_THAT_CANNOT_BE_DECODED"
    files = {"file": ("corrupted.jpg", corrupted_bytes, "image/jpeg")}
    response = client.post("/api/detect", files=files)
    assert response.status_code == 400
    assert "decode" in response.json()["detail"].lower() or "corrupted" in response.json()["detail"].lower()

def test_detect_non_image_file():
    """Test 5: Upload a non-image file (.txt / .pdf)."""
    text_bytes = b"Hello, this is just a plain text document, not an image."
    files = {"file": ("document.txt", text_bytes, "text/plain")}
    response = client.post("/api/detect", files=files)
    assert response.status_code == 400
    assert "unsupported file format" in response.json()["detail"].lower()

def test_detect_empty_file():
    """Test 6: Upload an empty file (0 bytes)."""
    files = {"file": ("empty.png", b"", "image/png")}
    response = client.post("/api/detect", files=files)
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()

def test_detect_oversized_file():
    """Test 7: Upload an image exceeding the size limit (15MB)."""
    # 16 MB dummy payload with valid extension
    oversized_bytes = b"\x00" * (16 * 1024 * 1024)
    files = {"file": ("huge.jpg", oversized_bytes, "image/jpeg")}
    response = client.post("/api/detect", files=files)
    assert response.status_code in [400, 413]
    assert "exceeds" in response.json()["detail"].lower()

def test_sequential_fresh_analysis():
    """Test 8: Confirm two sequential uploads return independent, fresh results."""
    # First image: Blue
    img1 = create_in_memory_image(format="JPEG", size=(100, 100), color=(0, 0, 255))
    resp1 = client.post("/api/detect", files={"file": ("blue.jpg", img1, "image/jpeg")})
    assert resp1.status_code == 200
    data1 = resp1.json()

    # Second image: Yellow
    img2 = create_in_memory_image(format="JPEG", size=(150, 150), color=(255, 255, 0))
    resp2 = client.post("/api/detect", files={"file": ("yellow.jpg", img2, "image/jpeg")})
    assert resp2.status_code == 200
    data2 = resp2.json()

    # Metadata must differ
    assert data1["image_metadata"]["filename"] == "blue.jpg"
    assert data2["image_metadata"]["filename"] == "yellow.jpg"
    assert data1["image_metadata"]["width"] == 100
    assert data2["image_metadata"]["width"] == 150

def test_v1_and_api_prefix_consistency():
    """Test 9: Both /api/detect and /api/v1/detect work identically."""
    img_bytes = create_in_memory_image(format="JPEG")
    r1 = client.post("/api/detect", files={"file": ("test.jpg", img_bytes, "image/jpeg")})
    r2 = client.post("/api/v1/detect", files={"file": ("test.jpg", img_bytes, "image/jpeg")})
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r1.json()["prediction"] == r2.json()["prediction"]
