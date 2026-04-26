"""AI inference service for eye disease classification.

This module handles model loading, image preprocessing, and prediction
with thread-safe singleton pattern for model management.
"""

import threading
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
from PIL import Image

if TYPE_CHECKING:
    import tensorflow as tf
    from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

# Model configuration
IMG_SIZE = 224
CLASS_NAMES = (
    "healthy_eye",
    "Conjunctivitis Recognition",
    "Cataract dataset",
    "keratitis",
)

# Thread-safe model loading
_model_lock = threading.Lock()
_model_cache: "tf.keras.Model | None" = None
_preprocess_fn = None


def _load_tensorflow_components():
    """Lazily load TensorFlow components to avoid import overhead."""
    global _preprocess_fn
    import tensorflow as tf  # noqa: PLC0415
    from tensorflow.keras.applications.mobilenet_v2 import preprocess_input  # noqa: PLC0415

    _preprocess_fn = preprocess_input
    return tf


def get_model(model_path: Path) -> "tf.keras.Model":
    """Get or load the ML model with thread-safe singleton pattern.

    Args:
        model_path: Path to the Keras model file.

    Returns:
        Loaded Keras model instance.

    Raises:
        FileNotFoundError: If model file doesn't exist.
        RuntimeError: If model loading fails.
    """
    global _model_cache

    if _model_cache is not None:
        return _model_cache

    with _model_lock:
        # Double-check after acquiring lock
        if _model_cache is not None:
            return _model_cache

        if not model_path.exists():
            raise FileNotFoundError(f"Model file not found at: {model_path}")

        try:
            tf = _load_tensorflow_components()
            _model_cache = tf.keras.models.load_model(str(model_path))
            # Warm up the model with a dummy input to avoid cold start latency
            _model_cache.predict(np.zeros((1, IMG_SIZE, IMG_SIZE, 3)), verbose=0)
        except Exception as e:
            raise RuntimeError(f"Failed to load model from {model_path}: {e}") from e

    return _model_cache


def _center_crop(image: Image.Image) -> Image.Image:
    """Apply center crop to extract the eye region.

    Crops the central 60% of the image (removing 20% from each edge).

    Args:
        image: PIL Image to crop.

    Returns:
        Cropped PIL Image.
    """
    width, height = image.size
    left = int(width * 0.2)
    top = int(height * 0.2)
    right = int(width * 0.8)
    bottom = int(height * 0.8)
    return image.crop((left, top, right, bottom))


def preprocess_image(image_path: str | Path) -> np.ndarray:
    """Preprocess an image for model inference.

    Pipeline:
    1. Load image and convert to RGB
    2. Apply center crop (60% of original)
    3. Resize to 224x224
    4. Convert to numpy array with float32 dtype
    5. Apply MobileNetV2 preprocessing
    6. Expand dimensions for batch inference

    Args:
        image_path: Path to the image file.

    Returns:
        Preprocessed image as numpy array with shape (1, 224, 224, 3).

    Raises:
        FileNotFoundError: If image file doesn't exist.
        ValueError: If image cannot be processed.
    """
    image_path = Path(image_path)
    if not image_path.exists():
        raise FileNotFoundError(f"Image file not found: {image_path}")

    try:
        # Load and convert to RGB
        image = Image.open(image_path).convert("RGB")

        # Apply center crop
        image = _center_crop(image)

        # Resize to model input size
        image = image.resize((IMG_SIZE, IMG_SIZE), Image.Resampling.LANCZOS)

        # Convert to numpy array
        array = np.asarray(image, dtype=np.float32)

        # Normalize to [0, 1]
        array = array / 255.0

        # Expand dimensions for batch (1, 224, 224, 3)
        return np.expand_dims(array, axis=0)

    except Exception as e:
        raise ValueError(f"Failed to preprocess image {image_path}: {e}") from e


def predict_image(image_path: str | Path, model_path: Path | None = None) -> tuple[str, float]:
    """Run inference on an image and return prediction with confidence.

    Args:
        image_path: Path to the image file for prediction.
        model_path: Optional path to model file (uses default if not provided).

    Returns:
        Tuple of (predicted_class_name, confidence_score).

    Raises:
        FileNotFoundError: If model or image file doesn't exist.
        RuntimeError: If prediction fails.
    """
    if model_path is None:
        from app.config import get_settings  # noqa: PLC0415

        model_path = get_settings().resolved_model_path

    try:
        model = get_model(model_path)
        batch = preprocess_image(image_path)

        # Run inference
        predictions = model.predict(batch, verbose=0)[0]

        # Extract prediction
        predicted_index = int(np.argmax(predictions))
        confidence = float(predictions[predicted_index])
        label = CLASS_NAMES[predicted_index]

        return label, confidence

    except (FileNotFoundError, ValueError):
        raise
    except Exception as e:
        raise RuntimeError(f"Prediction failed for image {image_path}: {e}") from e


def reset_model_cache() -> None:
    """Reset the model cache. Useful for testing or model reloading."""
    global _model_cache
    with _model_lock:
        _model_cache = None