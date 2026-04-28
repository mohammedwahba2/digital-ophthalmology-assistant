"""AI inference service for eye disease classification (Production Ready - HF Hub)."""

import threading
from pathlib import Path
from typing import TYPE_CHECKING
from huggingface_hub import snapshot_download

import numpy as np
from PIL import Image
import tensorflow as tf
from huggingface_hub import hf_hub_download

# ======================
# Config
# ======================

IMG_SIZE = 224

CLASS_NAMES = (
    "healthy_eye",
    "Conjunctivitis Recognition",
    "Cataract dataset",
    "keratitis",
)

MODEL_REPO = "mohamed-wahba77/eye-disease-model"
MODEL_FILE = "model.keras"

# ======================
# Singleton Model
# ======================

_model = None
_lock = threading.Lock()


def _download_model() -> str:
    """Download model from Hugging Face once."""
    return hf_hub_download(
        repo_id=MODEL_REPO,
        filename=MODEL_FILE
    )


def get_model() -> tf.keras.Model:
    """Thread-safe singleton model loader."""
    global _model

    if _model is not None:
        return _model

    with _lock:
        if _model is not None:
            return _model

        model_path = _download_model()
        _model = tf.keras.models.load_model(model_path)

        # warmup (important for DL latency)
        _model.predict(np.zeros((1, IMG_SIZE, IMG_SIZE, 3)), verbose=0)

    with _model_lock:
        # Double-check after acquiring lock
        if _model_cache is not None:
            return _model_cache

        if not model_path.exists():
            raise FileNotFoundError(f"Model file not found at: {model_path}")

        try:
            tf = _load_tensorflow_components()
            # _model_cache = tf.keras.models.load_model(str(model_path))
            # Warm up the model with a dummy input to avoid cold start latency
            local_dir = snapshot_download(repo_id="mohamed-wahba77/eye-disease-model")
            model_dir = Path(local_dir)
            # _model_cache.predict(np.zeros((1, IMG_SIZE, IMG_SIZE, 3)), verbose=0)
            _model_cache = tf.keras.models.load_model(str(model_dir))
            _model_cache.predict(np.zeros((1, IMG_SIZE, IMG_SIZE, 3)), verbose=0)
        except Exception as e:
            raise RuntimeError(f"Failed to load model from {model_path}: {e}") from e

    return _model_cache


# ======================
# Preprocessing
# ======================

def _center_crop(img: Image.Image) -> Image.Image:
    w, h = img.size
    return img.crop((w*0.2, h*0.2, w*0.8, h*0.8))


def preprocess_image(image_path: str | Path) -> np.ndarray:
    path = Path(image_path)

    if not path.exists():
        raise FileNotFoundError(f"Image not found: {path}")

    img = Image.open(path).convert("RGB")

    img = _center_crop(img)
    img = img.resize((IMG_SIZE, IMG_SIZE), Image.Resampling.LANCZOS)

    arr = np.asarray(img, dtype=np.float32) / 255.0

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