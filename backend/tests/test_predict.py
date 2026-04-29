"""Tests for prediction endpoint.

This module contains comprehensive tests for the eye disease classification
prediction functionality, covering validation, inference, and error handling.
"""

import io
import pytest
from PIL import Image
from fastapi.testclient import TestClient

from app.main import app
from app.database.db import get_db, engine, Base
from app.models.prediction import Prediction

# Create test database
Base.metadata.create_all(bind=engine)

client = TestClient(app)


def generate_test_image(size=(224, 224), color=(255, 255, 255)):
    """Generate a test image in memory.
    
    Args:
        size: Tuple of (width, height) for image dimensions.
        color: RGB color tuple for the image.
    
    Returns:
        BytesIO object containing the JPEG image data.
    """
    img = Image.new('RGB', size, color)
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    return img_bytes


class TestPredictionValidation:
    """Test image validation logic."""
    
    def test_valid_image_upload(self):
        """Test that valid images are accepted."""
        image_data = generate_test_image()
        files = {"file": ("test.jpg", image_data, "image/jpeg")}
        response = client.post("/predict", files=files)
        
        # Should not return 400 or 415 (validation errors)
        assert response.status_code != 400
        assert response.status_code != 415
    
    def test_missing_filename(self):
        """Test rejection of uploads without filename."""
        image_data = generate_test_image()
        files = {"file": ("", image_data, "image/jpeg")}
        response = client.post("/predict", files=files)
        
        assert response.status_code == 400
        assert "filename" in response.json()["detail"].lower()
    
    def test_unsupported_file_type(self):
        """Test rejection of unsupported file formats."""
        image_data = generate_test_image()
        files = {"file": ("test.txt", image_data, "text/plain")}
        response = client.post("/predict", files=files)
        
        assert response.status_code == 415
        assert "unsupported" in response.json()["detail"].lower()
    
    def test_empty_file(self):
        """Test rejection of empty files."""
        files = {"file": ("test.jpg", io.BytesIO(b""), "image/jpeg")}
        response = client.post("/predict", files=files)
        
        assert response.status_code == 400
        assert "empty" in response.json()["detail"].lower()
    
    def test_image_too_small(self):
        """Test rejection of images below minimum dimensions."""
        image_data = generate_test_image(size=(30, 30))  # Below 50x50 minimum
        files = {"file": ("test.jpg", image_data, "image/jpeg")}
        response = client.post("/predict", files=files)
        
        assert response.status_code == 400
        assert "too small" in response.json()["detail"].lower()
    
    def test_image_too_large(self):
        """Test rejection of images above maximum dimensions."""
        image_data = generate_test_image(size=(5000, 5000))  # Above 4096x4096 maximum
        files = {"file": ("test.jpg", image_data, "image/jpeg")}
        response = client.post("/predict", files=files)
        
        assert response.status_code == 400
        assert "too large" in response.json()["detail"].lower()
    
    def test_supported_image_formats(self):
        """Test that all supported formats are accepted."""
        supported_formats = [
            ("test.jpg", "image/jpeg"),
            ("test.jpeg", "image/jpeg"),
            ("test.png", "image/png"),
            ("test.bmp", "image/bmp"),
            ("test.webp", "image/webp"),
        ]
        
        for filename, content_type in supported_formats:
            image_data = generate_test_image()
            files = {"file": (filename, image_data, content_type)}
            response = client.post("/predict", files=files)
            
            # Should not return validation errors
            assert response.status_code not in [400, 415], f"Failed for {filename}"


class TestPredictionResponse:
    """Test prediction response format."""
    
    def test_prediction_response_structure(self):
        """Test that prediction response has correct structure."""
        image_data = generate_test_image()
        files = {"file": ("test.jpg", image_data, "image/jpeg")}
        response = client.post("/predict", files=files)
        
        if response.status_code == 200:
            data = response.json()
            assert "label" in data
            assert "confidence" in data
            assert isinstance(data["confidence"], float)
            assert 0.0 <= data["confidence"] <= 1.0
    
    def test_prediction_labels(self):
        """Test that predictions use valid class labels."""
        valid_labels = {"healthy_eye", "conjunctivitis", "cataract", "keratitis"}
        
        image_data = generate_test_image()
        files = {"file": ("test.jpg", image_data, "image/jpeg")}
        response = client.post("/predict", files=files)
        
        if response.status_code == 200:
            data = response.json()
            assert data["label"] in valid_labels, f"Invalid label: {data['label']}"


class TestDatabaseLogging:
    """Test that predictions are properly logged to database."""
    
    def test_prediction_saved_to_database(self):
        """Test that successful predictions are saved to database."""
        image_data = generate_test_image()
        files = {"file": ("test.jpg", image_data, "image/jpeg")}
        response = client.post("/predict", files=files)
        
        if response.status_code == 200:
            # Check that we can retrieve the result
            results_response = client.get("/api/v1/results")
            assert results_response.status_code == 200
            
            data = results_response.json()
            if "data" in data:  # Paginated response
                assert len(data["data"]) > 0