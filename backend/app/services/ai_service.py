"""AI inference service for eye disease classification (Deep Learning - HF Hub)."""

import threading
from pathlib import Path
from typing import Tuple

import numpy as np
from PIL import Image
import tensorflow as tf

# ======================
# Config
# ======================

IMG_SIZE = 224

CLASS_NAMES = (
    "healthy_eye",      # Index 0: Normal
    "conjunctivitis",   # Index 1: Conjunctivitis
    "cataract",         # Index 2: Cataract
    "keratitis",        # Index 3: Keratitis
)

# Confidence thresholds
HIGH_CONFIDENCE = 0.70  # Predictions above this are considered reliable
LOW_CONFIDENCE = 0.40   # Predictions below this should be flagged for review

# ======================
# Singleton DL Model
# ======================

_model = None
_lock = threading.Lock()

# Default local model path - points to the .keras directory
DEFAULT_MODEL_PATH = Path(__file__).resolve().parents[2] / "models" / "eye_disease_final_cropped.keras"

def _load_keras_model(model_path: Path) -> tf.keras.Model:
    """Load a Keras model from various formats.
    
    Supports:
    1. Standard .keras file (tf.keras.models.load_model)
    2. SavedModel format directory (tf.saved_model.load)
    3. Keras directory format (config.json + model.weights.h5)
    """
    import json
    
    # If it's a file, try standard loading
    if model_path.is_file():
        return tf.keras.models.load_model(str(model_path))
    
    # If it's a directory, check for different formats
    if model_path.is_dir():
        # Check for SavedModel format
        saved_model_pb = model_path / "saved_model.pb"
        if saved_model_pb.exists():
            return tf.saved_model.load(str(model_path))
        
        # Check for Keras directory format (config.json + weights)
        config_json = model_path / "config.json"
        weights_file = model_path / "model.weights.h5"
        if config_json.exists() and weights_file.exists():
            # Load model from JSON config
            with open(config_json) as f:
                model_json = f.read()
            model = tf.keras.models.model_from_json(model_json)
            # Load weights
            model.load_weights(str(weights_file))
            return model
        
        raise FileNotFoundError(f"No valid model found in directory: {model_path}")
    
    raise FileNotFoundError(f"Model path does not exist: {model_path}")


def get_model(model_path: Path | str | None = None) -> tf.keras.Model:
    """Thread-safe singleton DL model loader.
    
    Args:
        model_path: Optional local path to the model file. If not provided,
                   uses the default local path.
    
    Returns:
        Loaded TensorFlow Keras model.
    """
    global _model

    if _model is not None:
        return _model

    with _lock:
        if _model is not None:
            return _model

        if model_path is None:
            # Use default local model path
            model_path = DEFAULT_MODEL_PATH
        
        model_path = Path(model_path)
        
        try:
            _model = _load_keras_model(model_path)
        except Exception as e:
            raise RuntimeError(f"Failed to load model from {model_path}: {e}")

        # Warmup (important for DL inference latency)
        _model.predict(np.zeros((1, IMG_SIZE, IMG_SIZE, 3)), verbose=0)

    return _model


# ======================
# Preprocessing
# ======================

def _center_crop(img: Image.Image, crop_ratio: float = 0.6) -> Image.Image:
    """Custom Center Crop Algorithm for Ocular Focus.
    
    As described in the project methodology, this algorithm isolates the cornea 
    and lens region by cropping the central portion of the image, effectively 
    eliminating non-pathological noise such as eyelashes, skin, and lighting 
    artifacts from the periphery.
    
    Args:
        img: PIL Image to crop.
        crop_ratio: Ratio of the image to keep (default 0.6 = 60% center).
    
    Returns:
        Cropped PIL Image focused on the central ocular region.
    """
    w, h = img.size
    
    # Calculate crop boundaries to center on the ocular region
    # This removes peripheral noise (eyelashes, skin, equipment edges)
    left = w * (1 - crop_ratio) / 2
    top = h * (1 - crop_ratio) / 2
    right = w * (1 + crop_ratio) / 2
    bottom = h * (1 + crop_ratio) / 2
    
    return img.crop((left, top, right, bottom))


def preprocess_image(image_path: str | Path) -> np.ndarray:
    """Preprocess image for model inference.
    
    Matches the exact preprocessing used during training:
    1. Load image and convert to RGB
    2. Center crop (remove 20% from each side, keep 60% center)
    3. Resize to 224x224
    4. Normalize to [0, 1] by dividing by 255.0
    5. Expand dimensions for batch inference
    """
    path = Path(image_path)

    if not path.exists():
        raise FileNotFoundError(f"Image not found: {path}")

    # Load image and convert to RGB
    img = Image.open(path).convert("RGB")
    
    # Convert to numpy array for consistent processing
    arr = np.asarray(img, dtype=np.float32)
    
    h, w, _ = arr.shape

    # Center crop: remove 20% from each side (keep 60% center)
    start_h, start_w = int(h * 0.2), int(w * 0.2)
    end_h, end_w = int(h * 0.8), int(w * 0.8)
    
    arr = arr[start_h:end_h, start_w:end_w]

    # Resize to 224x224 using PIL for high-quality interpolation
    img = Image.fromarray(arr.astype(np.uint8))
    img = img.resize((224, 224), Image.Resampling.BILINEAR)
    
    # Convert back to numpy array and normalize
    arr = np.asarray(img, dtype=np.float32) / 255.0

    # Expand dimensions for batch inference (1, 224, 224, 3)
    return np.expand_dims(arr, axis=0)

    
# ======================
# Prediction
# ======================

def predict_image(image_path: str | Path) -> Tuple[str, float]:
    """Run inference on image and return prediction.
    
    Returns:
        Tuple of (class_name, confidence_score)
    """
    model = get_model()
    batch = preprocess_image(image_path)

    preds = model.predict(batch, verbose=0)[0]

    idx = int(np.argmax(preds))
    return CLASS_NAMES[idx], float(preds[idx])


def predict_image_detailed(image_path: str | Path) -> dict:
    """Run inference on image and return detailed prediction results.
    
    Returns all class probabilities and confidence level for better interpretability.
    
    Returns:
        Dictionary containing:
        - predicted_class: The predicted disease name
        - confidence: Confidence score for the prediction
        - confidence_level: "high", "medium", or "low"
        - all_probabilities: Dict of all class probabilities
        - needs_review: Boolean indicating if prediction should be reviewed
    """
    model = get_model()
    batch = preprocess_image(image_path)

    preds = model.predict(batch, verbose=0)[0]
    
    # Get predicted class and confidence
    idx = int(np.argmax(preds))
    predicted_class = CLASS_NAMES[idx]
    confidence = float(preds[idx])
    
    # Determine confidence level
    if confidence >= HIGH_CONFIDENCE:
        confidence_level = "high"
        needs_review = False
    elif confidence >= LOW_CONFIDENCE:
        confidence_level = "medium"
        needs_review = False
    else:
        confidence_level = "low"
        needs_review = True
    
    # Get all probabilities
    all_probabilities = {
        CLASS_NAMES[i]: float(preds[i]) for i in range(len(CLASS_NAMES))
    }
    
    return {
        "predicted_class": predicted_class,
        "confidence": round(confidence, 4),
        "confidence_level": confidence_level,
        "all_probabilities": {k: round(v, 4) for k, v in all_probabilities.items()},
        "needs_review": needs_review,
    }
