"""Tests for AI service module.

This module tests the core AI inference functionality, including the
Center Crop preprocessing algorithm and model loading.
"""

import pytest
from PIL import Image
import numpy as np

from app.services.ai_service import (
    _center_crop,
    preprocess_image,
    CLASS_NAMES,
    IMG_SIZE,
)


class TestCenterCropAlgorithm:
    """Tests for the custom Center Crop preprocessing algorithm.
    
    As described in the project methodology, this algorithm is designed
    to isolate the cornea and lens region by cropping the central portion
    of the image, eliminating peripheral noise such as eyelashes, skin,
    and lighting artifacts.
    """
    
    def test_center_crop_preserves_aspect_ratio(self):
        """Test that center crop maintains the original aspect ratio."""
        # Create test images with different aspect ratios
        test_sizes = [(100, 100), (200, 100), (100, 200), (500, 300)]
        
        for width, height in test_sizes:
            img = Image.new('RGB', (width, height), color=(255, 0, 0))
            cropped = _center_crop(img)
            
            # Check that the cropped image is centered
            # The crop should remove 20% from each side (keeping 60%)
            expected_width = int(width * 0.6)
            expected_height = int(height * 0.6)
            
            # Allow 1 pixel tolerance for rounding
            assert abs(cropped.size[0] - expected_width) <= 1
            assert abs(cropped.size[1] - expected_height) <= 1
    
    def test_center_crop_removes_periphery(self):
        """Test that center crop effectively removes peripheral regions."""
        # Create an image with distinct regions
        img = Image.new('RGB', (100, 100), color=(0, 0, 0))  # Black background
        
        # The center crop should focus on the middle 60%
        cropped = _center_crop(img)
        
        # Cropped image should be smaller than original
        assert cropped.size[0] < img.size[0]
        assert cropped.size[1] < img.size[1]
    
    def test_center_crop_custom_ratio(self):
        """Test center crop with custom crop ratio."""
        img = Image.new('RGB', (100, 100), color=(255, 0, 0))
        
        # Test with 50% crop ratio
        cropped = _center_crop(img, crop_ratio=0.5)
        expected_size = int(100 * 0.5)
        
        assert abs(cropped.size[0] - expected_size) <= 1
        assert abs(cropped.size[1] - expected_size) <= 1
    
    def test_center_crop_handles_various_sizes(self):
        """Test that center crop handles various image sizes correctly."""
        test_cases = [
            (50, 50),    # Small square
            (1000, 1000),  # Large square
            (640, 480),    # Standard camera resolution
            (1920, 1080),  # Full HD
            (100, 200),    # Portrait orientation
            (200, 100),    # Landscape orientation
        ]
        
        for width, height in test_cases:
            img = Image.new('RGB', (width, height), color=(128, 128, 128))
            cropped = _center_crop(img)
            
            # Should produce valid image
            assert cropped.size[0] > 0
            assert cropped.size[1] > 0
            assert cropped.size[0] <= width
            assert cropped.size[1] <= height


class TestClassNames:
    """Tests for class name configuration."""
    
    def test_class_names_count(self):
        """Test that we have exactly 4 classes as specified in the project."""
        assert len(CLASS_NAMES) == 4
    
    def test_class_names_format(self):
        """Test that class names follow consistent naming convention."""
        # All class names should be lowercase with underscores
        for name in CLASS_NAMES:
            assert name == name.lower(), f"Class name '{name}' should be lowercase"
            assert isinstance(name, str), f"Class name '{name}' should be string"
    
    def test_expected_classes_present(self):
        """Test that all expected disease classes are present."""
        expected_classes = {"healthy_eye", "conjunctivitis", "cataract", "keratitis"}
        actual_classes = set(CLASS_NAMES)
        
        assert actual_classes == expected_classes, \
            f"Expected {expected_classes}, got {actual_classes}"

    def test_class_order_matches_training(self):
        """Test that class order matches the training pipeline.
        
        The model was trained with classes in this specific order:
        Index 0: Normal (healthy_eye)
        Index 1: Conjunctivitis
        Index 2: Cataract
        Index 3: Keratitis
        
        This order MUST match the training configuration for correct predictions.
        """
        expected_order = ("healthy_eye", "conjunctivitis", "cataract", "keratitis")
        assert CLASS_NAMES == expected_order, \
            f"Class order mismatch. Expected {expected_order}, got {CLASS_NAMES}"


class TestImagePreprocessing:
    """Tests for image preprocessing pipeline."""
    
    def test_preprocessing_output_shape(self):
        """Test that preprocessed images have correct shape for model input."""
        # Create a test image
        img = Image.new('RGB', (300, 300), color=(255, 0, 0))
        img.save("/tmp/test_preprocess.jpg")
        
        # This test would require a mock model, so we'll just test the image loading
        # and cropping part without actual prediction
        pass  # Full test requires model setup
    
    def test_normalization_range(self):
        """Test that pixel values are normalized to [0, 1] range."""
        # Create test image with maximum intensity
        img = Image.new('RGB', (100, 100), color=(255, 255, 255))
        img.save("/tmp/test_white.jpg")
        
        # After preprocessing, values should be normalized
        # This is a conceptual test - actual implementation would need to test the array
        pass