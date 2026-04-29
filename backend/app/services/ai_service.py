"""AI inference service for eye disease classification (Deep Learning - HF Hub)."""

import threading
from pathlib import Path
from typing import Tuple

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
    "conjunctivitis",
    "cataract",
    "keratitis",
)

MODEL_REPO = "mohamed-wahba77/eye-disease-model"
MODEL_FILE = "model.keras"

# ======================
# Singleton DL Model
# ======================

_model = None
_lock = threading.Lock()


def _download_model() -> str:
    """Download DL model from Hugging Face Hub."""
    return hf_hub_download(
        repo_id=MODEL_REPO,
        filename=MODEL_FILE
    )


def get_model(model_path: Path | str | None = None) -> tf.keras.Model:
    """Thread-safe singleton DL model loader.
    
    Args:
        model_path: Optional local path to the model file. If not provided,
                   downloads from Hugging Face Hub.
    
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
            # Download from Hugging Face Hub
            model_path = _download_model()
        
        model_path = Path(model_path)
        
        if not model_path.exists():
            raise FileNotFoundError(f"Model file not found at: {model_path}")

        _model = tf.keras.models.load_model(str(model_path))

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