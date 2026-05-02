"""AI inference service for eye disease classification."""

import json
import math
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

# Load class names dynamically from training.
CLASS_PATH = Path(__file__).resolve().parents[2] / "models" / "class_names.json"

with open(CLASS_PATH) as f:
    CLASS_NAMES = tuple(json.load(f))

# Mapping from training labels to stable public API labels
CLASS_NAME_ALIASES = {
    "healthy_eye": "healthy_eye",
    "normal": "healthy_eye",
    "conjunctivitis recognition": "conjunctivitis",
    "conjunctivitis": "conjunctivitis",
    "cataract dataset": "cataract",
    "cataract": "cataract",
    "keratitis": "keratitis",
}

UNKNOWN_LABEL = "unrecognized"


def normalize_class_name(name: str) -> str:
    """Map notebook/training labels to stable public API labels."""
    normalized = "_".join(str(name).strip().lower().split())
    alias_key = normalized.replace("_", " ")
    return CLASS_NAME_ALIASES.get(alias_key, normalized)


# Normalized class names for API use (must be unique)
_NORMALIZED_CLASS_NAMES = tuple(normalize_class_name(name) for name in CLASS_NAMES)

if len(set(_NORMALIZED_CLASS_NAMES)) != len(_NORMALIZED_CLASS_NAMES):
    raise ValueError(
        "Normalized class names must remain unique. "
        f"Got raw={CLASS_NAMES!r}, normalized={_NORMALIZED_CLASS_NAMES!r}",
    )

# Confidence / abstention thresholds.
HIGH_CONFIDENCE = 0.80
MEDIUM_CONFIDENCE = 0.60
LOW_CONFIDENCE = 0.45
MIN_MARGIN = 0.15
MAX_NORMALIZED_ENTROPY = 0.85

# ======================
# Singleton DL Model
# ======================

_model = None
_lock = threading.Lock()

# Correct model path (matches training notebook).
DEFAULT_MODEL_PATH = Path(__file__).resolve().parents[2] / "models" / "Eye_Disease_model_v3.keras"


def get_model(model_path: Path | str | None = None) -> tf.keras.Model:
    global _model

    if _model is not None:
        return _model

    with _lock:
        if _model is not None:
            return _model

        if model_path is None:
            model_path = DEFAULT_MODEL_PATH

        model_path = Path(model_path)

        if not model_path.exists():
            raise FileNotFoundError(f"Model not found: {model_path}")

        _model = tf.keras.models.load_model(str(model_path))

        # Warmup
        _model.predict(np.zeros((1, IMG_SIZE, IMG_SIZE, 3)), verbose=0)

    return _model


# ======================
# Preprocessing (matches training pipeline 100%)
# ======================

def preprocess_image(image_path: str | Path) -> np.ndarray:
    """Preprocess image for model inference.
    
    Matches the exact preprocessing used during training:
    1. Load image and convert to RGB
    2. Scale so shortest side = 256 (maintaining aspect ratio)
    3. Center crop to 224x224
    4. Normalize to [0, 1] by dividing by 255.0
    5. Expand dimensions for batch inference
    """
    path = Path(image_path)

    if not path.exists():
        raise FileNotFoundError(f"Image not found: {path}")

    img = Image.open(path).convert("RGB")
    arr = np.asarray(img, dtype=np.float32)

    h, w = arr.shape[:2]

    # Scale to 256 on shortest side (same as training)
    scale = 256 / min(h, w)
    new_w, new_h = int(w * scale), int(h * scale)

    img = Image.fromarray(arr.astype(np.uint8))
    img = img.resize((new_w, new_h), Image.Resampling.BILINEAR)

    arr = np.asarray(img, dtype=np.float32)

    h, w = arr.shape[:2]

    # Center crop to 224x224
    start_h = (h - IMG_SIZE) // 2
    start_w = (w - IMG_SIZE) // 2

    arr = arr[start_h:start_h + IMG_SIZE, start_w:start_w + IMG_SIZE]

    # Normalize
    arr = arr / 255.0

    return np.expand_dims(arr, axis=0)


def _round_probability(value: float) -> float:
    """Keep enough precision so small probabilities do not collapse to zero."""
    return round(float(value), 6)


def _normalized_entropy(probabilities: np.ndarray) -> float:
    """Return entropy scaled to [0, 1]. High entropy means uncertain output."""
    probs = np.clip(probabilities.astype(np.float64), 1e-12, 1.0)
    entropy = -np.sum(probs * np.log(probs))
    return float(entropy / math.log(len(probs)))


def build_prediction_result(probabilities: np.ndarray) -> dict:
    """Convert raw softmax output into a safer API response."""
    probs = np.asarray(probabilities, dtype=np.float32)
    if probs.ndim != 1 or len(probs) != len(CLASS_NAMES):
        raise ValueError(
            f"Expected {len(CLASS_NAMES)} class probabilities, got shape={probs.shape}",
        )

    sorted_indices = np.argsort(probs)[::-1]
    top_idx = int(sorted_indices[0])
    top_prob = float(probs[top_idx])
    second_prob = float(probs[sorted_indices[1]]) if len(sorted_indices) > 1 else 0.0
    margin = top_prob - second_prob
    entropy = _normalized_entropy(probs)

    # Use normalized class name for the predicted class
    predicted_class = normalize_class_name(CLASS_NAMES[top_idx])
    is_low_confidence = top_prob < LOW_CONFIDENCE
    is_ambiguous = margin < MIN_MARGIN
    is_high_entropy = entropy > MAX_NORMALIZED_ENTROPY
    needs_review = is_low_confidence or is_ambiguous or is_high_entropy

    if top_prob >= HIGH_CONFIDENCE and margin >= MIN_MARGIN:
        confidence_level = "high"
    elif top_prob >= MEDIUM_CONFIDENCE and margin >= MIN_MARGIN:
        confidence_level = "medium"
    else:
        confidence_level = "low"

    public_label = UNKNOWN_LABEL if needs_review else predicted_class
    
    # Build probabilities dict with normalized class names
    all_probabilities = {
        normalize_class_name(CLASS_NAMES[i]): _round_probability(probs[i]) 
        for i in range(len(CLASS_NAMES))
    }

    return {
        "label": public_label,
        "predicted_class": predicted_class,
        "confidence": _round_probability(top_prob),
        "confidence_level": confidence_level,
        "all_probabilities": all_probabilities,
        "needs_review": needs_review,
        "second_best_class": normalize_class_name(CLASS_NAMES[int(sorted_indices[1])]) if len(sorted_indices) > 1 else predicted_class,
        "second_best_confidence": _round_probability(second_prob),
        "confidence_margin": _round_probability(margin),
        "normalized_entropy": _round_probability(entropy),
    }


# ======================
# Prediction
# ======================

def predict_image(image_path: str | Path) -> Tuple[str, float]:
    """Run inference on image and return prediction.
    
    Returns:
        Tuple of (label, confidence_score)
    """
    model = get_model()
    batch = preprocess_image(image_path)

    preds = model.predict(batch, verbose=0)[0]
    result = build_prediction_result(preds)
    return result["label"], float(result["confidence"])


def predict_image_detailed(image_path: str | Path) -> dict:
    """Run inference on image and return detailed prediction results.
    
    Returns all class probabilities and confidence metrics.
    """
    model = get_model()
    batch = preprocess_image(image_path)

    preds = model.predict(batch, verbose=0)[0]
    return build_prediction_result(preds)
