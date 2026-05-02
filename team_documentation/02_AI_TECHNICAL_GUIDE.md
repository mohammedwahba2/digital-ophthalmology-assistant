# AI/Deep Learning Technical Guide

##  Overview

This document provides a comprehensive technical guide to the Deep Learning system used for eye disease classification.

---

##  Table of Contents

1. [Model Architecture](#model-architecture)
2. [Inference Pipeline](#inference-pipeline)
3. [Code Implementation](#code-implementation)
4. [Model Loading](#model-loading)
5. [Preprocessing](#preprocessing)
6. [Prediction](#prediction)
7. [Performance Optimization](#performance-optimization)
8. [Troubleshooting](#troubleshooting)

---

## Model Architecture

### Base Architecture: MobileNetV2

Our model is built on **MobileNetV2**, a lightweight convolutional neural network designed for mobile and embedded vision applications.

#### Why MobileNetV2?
- **Efficiency**: Optimized for mobile and web deployment
- **Speed**: Fast inference time (~2-3 seconds per image)
- **Accuracy**: Good balance between size and performance
- **Depthwise Separable Convolutions**: Reduces parameters and computation

### Model Specifications

| Parameter | Value |
|-----------|-------|
| **Input Shape** | 224 × 224 × 3 (RGB) |
| **Base Architecture** | MobileNetV2 (pre-trained on ImageNet) |
| **Custom Layers** | Global Average Pooling + BatchNormalization + Dense(256) + Dropout(0.5) + Dense(128) + Dropout(0.3) + Dense(4, softmax) |
| **Output Classes** | 4 (Healthy, Conjunctivitis, Cataract, Keratitis) |
| **Model Format** | `.keras` (Keras native format) |
| **Model File** | `Eye_Disease_model_v3.keras` |
| **Model Size** | ~22 MB |
| **Training Dataset** | Custom eye disease image dataset |
| **Class Names (Training)** | `["healthy_eye", "Conjunctivitis Recognition", "Cataract dataset", "keratitis"]` |
| **Class Names (API)** | `["healthy_eye", "conjunctivitis", "cataract", "keratitis"]` |

### Model Architecture Diagram

```
Input (224×224×3)
    ↓
MobileNetV2 Base (pre-trained weights)
    ↓
Global Average Pooling 2D
    ↓
Dropout (0.5)
    ↓
Dense Layer (4 units, softmax activation)
    ↓
Output Probabilities [p_healthy, p_conjunctivitis, p_cataract, p_keratitis]
```

---

## Inference Pipeline

The complete inference process consists of 5 stages:

```
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 1: Image Upload                                          │
│ - User selects/drags image file                                │
│ - Frontend validates file type (JPG, PNG, etc.)                │
│ - File size check (max 10MB)                                   │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 2: Backend Reception                                     │
│ - FastAPI receives multipart form data                         │
│ - Validates file extension and content                         │
│ - Saves to temporary upload directory                          │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 3: Image Preprocessing                                   │
│ - Load image with Pillow                                       │
│ - Convert to RGB (remove alpha channel if present)             │
│ - Scale: shortest side → 256 (maintain aspect ratio)           │
│ - Center crop to 224×224 pixels                                │
│ - Normalize pixel values (divide by 255.0)                     │
│ - Expand dimensions for batch inference                        │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 4: Model Inference                                       │
│ - Load pre-trained model (singleton pattern)                   │
│ - Run forward pass through neural network                      │
│ - Get output probabilities for each class                      │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 5: Post-processing & Response                            │
│ - Normalize class names (training → API labels)                │
│ - Compute confidence metrics (margin, entropy)                 │
│ - Determine confidence level (high/medium/low)                 │
│ - Flag low-confidence predictions for review                   │
│ - Return JSON response with all probabilities                  │
│ - Save prediction to database for history                      │
└─────────────────────────────────────────────────────────────────┘
```

---

## Code Implementation

### File Structure

```
backend/app/services/
├── __init__.py
├── ai_service.py          # Main AI service (this is the core)
└── seed_service.py        # Database seeding
```

### Core AI Service: `ai_service.py`

#### 1. Imports and Configuration

```python
import json
import math
import threading
from pathlib import Path
from typing import Tuple

import numpy as np
from PIL import Image
import tensorflow as tf

# Configuration constants
IMG_SIZE = 224

# Load class names dynamically from training (stored in class_names.json)
CLASS_PATH = Path(__file__).resolve().parents[2] / "models" / "class_names.json"
with open(CLASS_PATH) as f:
    CLASS_NAMES = tuple(json.load(f))
# CLASS_NAMES = ("healthy_eye", "Conjunctivitis Recognition", "Cataract dataset", "keratitis")

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

# Confidence thresholds
HIGH_CONFIDENCE = 0.80
MEDIUM_CONFIDENCE = 0.60
LOW_CONFIDENCE = 0.45
MIN_MARGIN = 0.15
MAX_NORMALIZED_ENTROPY = 0.85
```

#### 2. Model Loading (Singleton Pattern)

```python
_model = None
_lock = threading.Lock()

DEFAULT_MODEL_PATH = Path(__file__).resolve().parents[2] / "models" / "Eye_Disease_model_v3.keras"

def get_model(model_path: Path | str | None = None) -> tf.keras.Model:
    """Thread-safe singleton DL model loader."""
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

        # Warmup (important for DL inference latency)
        _model.predict(np.zeros((1, IMG_SIZE, IMG_SIZE, 3)), verbose=0)

    return _model
```

**Key Points:**
- **Singleton Pattern**: Model is loaded only once, then reused
- **Thread Safety**: Lock prevents race conditions during loading
- **Lazy Loading**: Model loads on first use, not at startup
- **Warmup**: First prediction prepares GPU/CPU for faster subsequent inferences

#### 3. Image Preprocessing (Matches Training 100%)

```python
def preprocess_image(image_path: str | Path) -> np.ndarray:
    """Prepare image for model inference.
    
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
```

**Why Scale to 256 First?**
- Maintains aspect ratio (no distortion)
- Ensures consistent preprocessing with training
- The model was trained with this exact scaling approach

**Why Center Crop to 224?**
- Focuses on the central ocular region
- Removes peripheral noise (eyelashes, skin, equipment edges)
- Matches the model's input requirements

**Why Normalize?**
- Neural networks train better with normalized inputs
- Pixel values in [0, 1] range stabilize gradient descent
- Matches preprocessing used during model training

#### 4. Prediction with Enhanced Post-Processing

```python
def build_prediction_result(probabilities: np.ndarray) -> dict:
    """Convert raw softmax output into a safer API response."""
    probs = np.asarray(probabilities, dtype=np.float32)
    
    sorted_indices = np.argsort(probs)[::-1]
    top_idx = int(sorted_indices[0])
    top_prob = float(probs[top_idx])
    second_prob = float(probs[sorted_indices[1]]) if len(sorted_indices) > 1 else 0.0
    margin = top_prob - second_prob
    entropy = _normalized_entropy(probs)

    # Use normalized class name for the predicted class
    predicted_class = normalize_class_name(CLASS_NAMES[top_idx])
    
    # Determine if prediction needs review
    is_low_confidence = top_prob < LOW_CONFIDENCE
    is_ambiguous = margin < MIN_MARGIN
    is_high_entropy = entropy > MAX_NORMALIZED_ENTROPY
    needs_review = is_low_confidence or is_ambiguous or is_high_entropy

    # Determine confidence level
    if top_prob >= HIGH_CONFIDENCE and margin >= MIN_MARGIN:
        confidence_level = "high"
    elif top_prob >= MEDIUM_CONFIDENCE and margin >= MIN_MARGIN:
        confidence_level = "medium"
    else:
        confidence_level = "low"

    public_label = UNKNOWN_LABEL if needs_review else predicted_class
    
    return {
        "label": public_label,
        "predicted_class": predicted_class,
        "confidence": round(top_prob, 6),
        "confidence_level": confidence_level,
        "all_probabilities": {
            normalize_class_name(CLASS_NAMES[i]): round(float(probs[i]), 6) 
            for i in range(len(CLASS_NAMES))
        },
        "needs_review": needs_review,
        "second_best_class": normalize_class_name(CLASS_NAMES[sorted_indices[1]]),
        "second_best_confidence": round(second_prob, 6),
        "confidence_margin": round(margin, 6),
        "normalized_entropy": round(entropy, 6),
    }

def predict_image(image_path: str | Path) -> Tuple[str, float]:
    """Run inference on image and return prediction."""
    model = get_model()
    batch = preprocess_image(image_path)
    preds = model.predict(batch, verbose=0)[0]
    result = build_prediction_result(preds)
    return result["label"], float(result["confidence"])

def predict_image_detailed(image_path: str | Path) -> dict:
    """Run inference and return detailed prediction results."""
    model = get_model()
    batch = preprocess_image(image_path)
    preds = model.predict(batch, verbose=0)[0]
    return build_prediction_result(preds)
```

**Output Explanation:**
- `label`: The public-facing prediction (or "unrecognized" if low confidence)
- `predicted_class`: The actual model prediction (normalized class name)
- `confidence`: Confidence score for the prediction
- `confidence_level`: "high", "medium", or "low"
- `all_probabilities`: Full probability distribution over all classes
- `needs_review`: Boolean flag for low-confidence predictions
- Additional metrics: margin, entropy, second-best class

---

## Model Loading

### Option 1: Automatic Download from Hugging Face Hub

```python
from app.services.ai_service import get_model

# No argument = download from HF Hub
model = get_model()
```

### Option 2: Local Model Path

```python
from pathlib import Path
from app.services.ai_service import get_model

# Provide local path
model = get_model(Path("backend/models/model.keras"))
```

### Option 3: Configuration-Based Loading

```python
# In config.py
@property
def resolved_model_path(self) -> Path:
    """Get default local model path."""
    return Path(__file__).resolve().parents[2] / "models" / self.model_filename

# In main.py (startup)
from app.services.ai_service import get_model
get_model(settings.resolved_model_path)
```

---

## Preprocessing Details

### Step-by-Step Transformation

| Step | Operation | Input Shape | Output Shape | Purpose |
|------|-----------|-------------|--------------|---------|
| 1 | Load Image | File on disk | (H, W, 3) | Read image data |
| 2 | Convert to RGB | (H, W, 4) or (H, W) | (H, W, 3) | Ensure 3 channels |
| 3 | Scale (shortest=256) | (H, W, 3) | (H', W', 3) | Maintain aspect ratio |
| 4 | Center Crop | (H', W', 3) | (224, 224, 3) | Focus on eye region |
| 5 | Normalize | [0, 255] | [0.0, 1.0] | Stabilize inference |
| 6 | Expand Dims | (224, 224, 3) | (1, 224, 224, 3) | Add batch dimension |

### Visual Example

```
Original Image (1000×800)
    ↓ Scale (shortest side → 256)
Scaled Image (320×256) - aspect ratio preserved
    ↓ Center Crop (224×224 from center)
Cropped Image (224×224) - focused on center
    ↓ Normalize
Normalized Image - pixel values between 0 and 1
    ↓ Expand Dims
Batch Image (1, 224, 224, 3) - ready for model
```

### Class Name Normalization

The model was trained with specific folder names that differ from the API labels:

| Training Label (from class_names.json) | API Label (normalized) |
|----------------------------------------|------------------------|
| `healthy_eye` | `healthy_eye` |
| `Conjunctivitis Recognition` | `conjunctivitis` |
| `Cataract dataset` | `cataract` |
| `keratitis` | `keratitis` |

The `normalize_class_name()` function handles this mapping to ensure consistent API responses.

---

## Prediction

### Understanding Model Output

The model outputs a probability distribution over 4 classes:

```python
# Example output (raw probabilities)
preds = [0.9234, 0.0421, 0.0234, 0.0111]
#          healthy   conjunctivitis  cataract  keratitis

# Interpretation:
# - 92.34% chance: Healthy eye
# - 4.21% chance: Conjunctivitis
# - 2.34% chance: Cataract
# - 1.11% chance: Keratitis

# Full API response:
{
    "label": "healthy_eye",           # Public-facing label
    "predicted_class": "healthy_eye", # Normalized class name
    "confidence": 0.9234,
    "confidence_level": "high",
    "needs_review": False,
    "all_probabilities": {
        "healthy_eye": 0.9234,
        "conjunctivitis": 0.0421,
        "cataract": 0.0234,
        "keratitis": 0.0111
    },
    "second_best_class": "conjunctivitis",
    "confidence_margin": 0.8813,
    "normalized_entropy": 0.1523
}
```

### Confidence Thresholds

| Threshold | Value | Interpretation |
|-----------|-------|----------------|
| `HIGH_CONFIDENCE` | 0.80 | Prediction is reliable |
| `MEDIUM_CONFIDENCE` | 0.60 | Prediction is moderately reliable |
| `LOW_CONFIDENCE` | 0.45 | Prediction is uncertain |
| `MIN_MARGIN` | 0.15 | Minimum gap between top 2 classes |
| `MAX_NORMALIZED_ENTROPY` | 0.85 | Maximum uncertainty (entropy) |

### Confidence Levels

| Level | Conditions | Action |
|-------|------------|--------|
| `high` | confidence ≥ 0.80 AND margin ≥ 0.15 | Trust prediction |
| `medium` | confidence ≥ 0.60 AND margin ≥ 0.15 | Consider prediction, verify clinically |
| `low` | Otherwise | Flag for review, recommend specialist |

### Low-Confidence Detection

A prediction is flagged for review (`needs_review=True`) if ANY of:
- Top probability < `LOW_CONFIDENCE` (0.45)
- Margin between top 2 classes < `MIN_MARGIN` (0.15)
- Normalized entropy > `MAX_NORMALIZED_ENTROPY` (0.85)

When flagged, the `label` field returns `"unrecognized"` instead of the predicted class.

---

## Performance Optimization

### 1. Model Warmup

```python
# First prediction after loading is slow (cold start)
# Warmup prepares the model
_model.predict(np.zeros((1, IMG_SIZE, IMG_SIZE, 3)), verbose=0)
```

### 2. Singleton Pattern

```python
# Load once, use many times
# Saves memory and loading time
_model = None  # Global variable
```

### 3. Thread Safety

```python
_lock = threading.Lock()  # Prevents race conditions

with _lock:
    # Only one thread can load model at a time
    if _model is None:
        _model = load_model()
```

### 4. Batch Inference (Future Enhancement)

```python
# Currently: One image at a time
# Future: Multiple images in one batch
batch = np.vstack([img1, img2, img3])  # (3, 224, 224, 3)
preds = model.predict(batch)  # Faster than 3 separate predictions
```

### Performance Metrics

| Metric | Value | Notes |
|--------|-------|-------|
| Model Load Time | ~2-3 seconds | One-time cost |
| Inference Time | ~0.5-1 second | Per image |
| Memory Usage | ~200 MB | Model + overhead |
| CPU Usage | ~50-80% | During inference |

---

## Troubleshooting

### Issue 1: Model Not Found

**Error:**
```
FileNotFoundError: Model file not found at: /path/to/model.keras
```

**Solutions:**
1. Ensure model file exists at specified path
2. Check file permissions
3. Verify Hugging Face Hub access if downloading

### Issue 2: Out of Memory

**Error:**
```
ResourceExhaustedError: OOM when allocating tensor
```

**Solutions:**
1. Reduce batch size (currently 1, cannot reduce further)
2. Use CPU instead of GPU: `export CUDA_VISIBLE_DEVICES=""`
3. Close other memory-intensive applications

### Issue 3: Slow Inference

**Symptoms:**
- Prediction takes >5 seconds
- High CPU usage

**Solutions:**
1. Ensure model warmup is performed
2. Check system resources (RAM, CPU)
3. Consider using GPU acceleration
4. Optimize image preprocessing (resize before upload)

### Issue 4: Poor Predictions

**Symptoms:**
- Low confidence scores
- Incorrect classifications

**Solutions:**
1. Verify image quality (good lighting, focus)
2. Ensure proper preprocessing (center crop, normalize)
3. Check if image is actually an eye image
4. Consider model retraining with more data

---

## API Usage Example

### Request

```bash
curl -X POST http://localhost:8000/predict \
  -F "file=@/path/to/eye_image.jpg"
```

### Response

```json
{
  "label": "healthy_eye",
  "predicted_class": "healthy_eye",
  "confidence": 0.9234,
  "confidence_level": "high",
  "all_probabilities": {
    "healthy_eye": 0.9234,
    "conjunctivitis": 0.0421,
    "cataract": 0.0234,
    "keratitis": 0.0111
  },
  "needs_review": false,
  "second_best_class": "conjunctivitis",
  "second_best_confidence": 0.0421,
  "confidence_margin": 0.8813,
  "normalized_entropy": 0.1523
}
```

### Python Client

```python
import requests

# Upload image
with open("eye_image.jpg", "rb") as f:
    files = {"file": f}
    response = requests.post("http://localhost:8000/predict", files=files)

# Parse response
result = response.json()
print(f"Prediction: {result['label']}")
print(f"Confidence: {result['confidence']:.2%}")
```

---

## Future Enhancements

### 1. Multi-Model Ensemble
```python
# Combine predictions from multiple models for better accuracy
models = [model1, model2, model3]
predictions = [m.predict(batch) for m in models]
final_pred = np.mean(predictions, axis=0)
```

### 2. Grad-CAM Visualization
```python
# Show which parts of the image influenced the prediction
# Helps with model interpretability and clinical trust
```

### 3. Uncertainty Quantification
```python
# Provide confidence intervals, not just point estimates
# Helps clinicians understand prediction reliability
```

### 4. Model Versioning
```python
# Track model versions and allow rollback
# A/B testing of different model versions
```

---

## Key Takeaways

1. **Model**: MobileNetV2-based CNN with custom head (BatchNorm, Dense layers, Dropout)
2. **Input**: 224×224 RGB images, scaled to 256 shortest side then center-cropped
3. **Output**: 4-class classification with enhanced confidence metrics
4. **Class Names**: Training labels normalized to stable API labels via `normalize_class_name()`
5. **Performance**: ~1 second inference time, singleton pattern for efficiency
6. **Safety**: Low-confidence predictions flagged with `needs_review=True` and `label="unrecognized"`
7. **Model File**: `Eye_Disease_model_v3.keras` (~22 MB)
8. **Class Names File**: `class_names.json` (dynamic loading prevents mismatch)

---

*For questions about the AI system, contact the AI/ML team lead.*

*Last Updated: May 3, 2026*  
*Document Version: 2.0*
