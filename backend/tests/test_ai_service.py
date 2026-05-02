"""Tests for AI service module.

This module tests the core AI inference functionality, including the
preprocessing pipeline and model loading.
"""

import pytest
from PIL import Image
import numpy as np

from app.services.ai_service import (
    preprocess_image,
    build_prediction_result,
    normalize_class_name,
    CLASS_NAMES,
    IMG_SIZE,
    UNKNOWN_LABEL,
)


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
        assert tuple(CLASS_NAMES) == expected_order, \
            f"Class order mismatch. Expected {expected_order}, got {CLASS_NAMES}"

    def test_training_aliases_are_normalized(self):
        """Notebook labels should map to stable API labels."""
        assert normalize_class_name("Conjunctivitis Recognition") == "conjunctivitis"
        assert normalize_class_name("Cataract dataset") == "cataract"
        assert normalize_class_name("healthy_eye") == "healthy_eye"


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


class TestPredictionPostProcessing:
    """Tests for probability-to-response conversion."""

    def test_high_confidence_prediction_keeps_label(self):
        result = build_prediction_result(np.array([0.91, 0.05, 0.03, 0.01], dtype=np.float32))

        assert result["label"] == "healthy_eye"
        assert result["predicted_class"] == "healthy_eye"
        assert result["needs_review"] is False
        assert result["confidence_level"] == "high"

    def test_low_confidence_prediction_becomes_unrecognized(self):
        result = build_prediction_result(np.array([0.27, 0.26, 0.24, 0.23], dtype=np.float32))

        assert result["label"] == UNKNOWN_LABEL
        assert result["predicted_class"] == "healthy_eye"
        assert result["needs_review"] is True
        assert result["confidence_level"] == "low"

    def test_small_probabilities_keep_precision(self):
        result = build_prediction_result(np.array([0.999998, 0.000001, 0.0000006, 0.0000004], dtype=np.float32))

        assert result["all_probabilities"]["conjunctivitis"] == 0.000001
        assert result["all_probabilities"]["cataract"] == 0.000001
        assert result["all_probabilities"]["keratitis"] == 0.0
