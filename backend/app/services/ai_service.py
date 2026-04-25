from pathlib import Path

import numpy as np
import tensorflow as tf
from PIL import Image
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

IMG_SIZE = 224
CLASS_NAMES = (
    "healthy_eye",
    "Conjunctivitis Recognition",
    "Cataract dataset",
    "keratitis",
)
MODEL_PATH = Path(__file__).resolve().parents[2] / "models" / "eye_disease_final_cropped.keras"

_MODEL = None


def _load_model():
    global _MODEL
    if _MODEL is not None:
        return _MODEL

    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Inference model not found at {MODEL_PATH}")

    _MODEL = tf.keras.models.load_model(MODEL_PATH)
    return _MODEL


def _center_crop(image: Image.Image) -> Image.Image:
    width, height = image.size
    left = int(width * 0.2)
    top = int(height * 0.2)
    right = int(width * 0.8)
    bottom = int(height * 0.8)
    return image.crop((left, top, right, bottom))


def _preprocess_image(image_path: str) -> np.ndarray:
    image = Image.open(image_path).convert("RGB")
    image = _center_crop(image)
    image = image.resize((IMG_SIZE, IMG_SIZE))
    array = np.asarray(image, dtype=np.float32)
    array = preprocess_input(array)
    return np.expand_dims(array, axis=0)


def predict_image(image_path: str):
    model = _load_model()
    batch = _preprocess_image(image_path)
    scores = model.predict(batch, verbose=0)[0]

    predicted_index = int(np.argmax(scores))
    confidence = float(scores[predicted_index])
    label = CLASS_NAMES[predicted_index]

    return label, confidence
