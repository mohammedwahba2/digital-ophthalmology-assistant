"""
AI inference service for eye disease classification
(Aligned with training pipeline - MobileNetV2 v2)
"""

import threading
from pathlib import Path
from typing import Tuple
import json

import numpy as np
from PIL import Image
import tensorflow as tf

# ======================
# Config
# ======================

IMG_SIZE = 224

# 🔥 Load class names dynamically (prevents mismatch)
CLASS_PATH = Path(__file__).resolve().parents[2] / "models" / "class_names.json"

with open(CLASS_PATH) as f:
    CLASS_NAMES = json.load(f)

# Confidence thresholds
HIGH_CONFIDENCE = 0.70
LOW_CONFIDENCE = 0.40

# ======================
# Singleton DL Model
# ======================

_model = None
_lock = threading.Lock()

# 🔥 Correct model path (NEW MODEL)
DEFAULT_MODEL_PATH = Path(__file__).resolve().parents[2] / "models" / "eye_disease_model_v2.keras"


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
# Preprocessing (🔥 مطابق للموديل 100%)
# ======================

def preprocess_image(image_path: str | Path) -> np.ndarray:
    path = Path(image_path)

    if not path.exists():
        raise FileNotFoundError(f"Image not found: {path}")

    # Load image
    img = Image.open(path).convert("RGB")
    arr = np.asarray(img, dtype=np.float32)

    h, w = arr.shape[:2]

    # 🔥 SAME AS TRAINING
    scale = 256 / min(h, w)
    new_w, new_h = int(w * scale), int(h * scale)

    img = Image.fromarray(arr.astype(np.uint8))
    img = img.resize((new_w, new_h), Image.Resampling.BILINEAR)

    arr = np.asarray(img, dtype=np.float32)

    h, w = arr.shape[:2]

    start_h = (h - IMG_SIZE) // 2
    start_w = (w - IMG_SIZE) // 2

    arr = arr[start_h:start_h + IMG_SIZE, start_w:start_w + IMG_SIZE]

    # Normalize
    arr = arr / 255.0

    # Expand dims
    return np.expand_dims(arr, axis=0)


# ======================
# Prediction
# ======================

def predict_image(image_path: str | Path) -> Tuple[str, float]:
    model = get_model()
    batch = preprocess_image(image_path)

    preds = model.predict(batch, verbose=0)[0]

    idx = int(np.argmax(preds))
    return CLASS_NAMES[idx], float(preds[idx])


def predict_image_detailed(image_path: str | Path) -> dict:
    model = get_model()
    batch = preprocess_image(image_path)

    preds = model.predict(batch, verbose=0)[0]

    idx = int(np.argmax(preds))
    predicted_class = CLASS_NAMES[idx]
    confidence = float(preds[idx])

    # Confidence level
    if confidence >= HIGH_CONFIDENCE:
        confidence_level = "high"
        needs_review = False
    elif confidence >= LOW_CONFIDENCE:
        confidence_level = "medium"
        needs_review = False
    else:
        confidence_level = "low"
        needs_review = True

    # All probabilities
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
