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
| **Custom Layers** | Global Average Pooling + Dense (4 units, softmax) |
| **Output Classes** | 4 (Healthy, Conjunctivitis, Cataract, Keratitis) |
| **Model Format** | `.keras` (Keras native format) |
| **Model Size** | ~14 MB |
| **Training Dataset** | Custom eye disease image dataset |

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
│ - Center crop (60% of original image)                          │
│ - Resize to 224×224 pixels                                     │
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
│ - Find class with highest probability                          │
│ - Extract confidence score                                     │
│ - Map class index to disease name                              │
│ - Return JSON response with label and confidence               │
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
import threading
from pathlib import Path
from typing import Tuple

import numpy as np
from PIL import Image
import tensorflow as tf
from huggingface_hub import hf_hub_download

# Configuration constants
IMG_SIZE = 224
CLASS_NAMES = (
    "healthy_eye",
    "Conjunctivitis Recognition",
    "Cataract dataset",
    "keratitis",
)
MODEL_REPO = "mohamed-wahba77/eye-disease-model"
MODEL_FILE = "model.keras"
```

#### 2. Model Loading (Singleton Pattern)

```python
_model = None
_lock = threading.Lock()

def get_model(model_path: Path | str | None = None) -> tf.keras.Model:
    """Thread-safe singleton DL model loader."""
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
```

**Key Points:**
- **Singleton Pattern**: Model is loaded only once, then reused
- **Thread Safety**: Lock prevents race conditions during loading
- **Lazy Loading**: Model loads on first use, not at startup
- **Warmup**: First prediction prepares GPU/CPU for faster subsequent inferences

#### 3. Image Preprocessing

```python
def _center_crop(img: Image.Image) -> Image.Image:
    """Crop center 60% of image."""
    w, h = img.size
    return img.crop((w*0.2, h*0.2, w*0.8, h*0.8))

def preprocess_image(image_path: str | Path) -> np.ndarray:
    """Prepare image for model inference."""
    path = Path(image_path)

    if not path.exists():
        raise FileNotFoundError(f"Image not found: {path}")

    # Load and convert to RGB
    img = Image.open(path).convert("RGB")

    # Center crop and resize
    img = _center_crop(img)
    img = img.resize((IMG_SIZE, IMG_SIZE), Image.Resampling.LANCZOS)

    # Normalize to [0, 1]
    arr = np.asarray(img, dtype=np.float32) / 255.0

    # Add batch dimension: (224, 224, 3) → (1, 224, 224, 3)
    return np.expand_dims(arr, axis=0)
```

**Why Center Crop?**
- Removes peripheral distractions
- Focuses on the eye region
- Improves model accuracy by removing irrelevant background

**Why Normalize?**
- Neural networks train better with normalized inputs
- Pixel values in [0, 1] range stabilize gradient descent
- Matches preprocessing used during model training

#### 4. Prediction Function

```python
def predict_image(image_path: str | Path) -> Tuple[str, float]:
    """Run inference on image and return prediction."""
    model = get_model()
    batch = preprocess_image(image_path)

    # Get model predictions
    preds = model.predict(batch, verbose=0)[0]

    # Find class with highest probability
    idx = int(np.argmax(preds))
    
    # Return class name and confidence score
    return CLASS_NAMES[idx], float(preds[idx])
```

**Output Explanation:**
- Returns tuple: `(disease_name, confidence_score)`
- Example: `("healthy_eye", 0.9234)` means 92.34% confidence it's healthy

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
| 3 | Center Crop | (H, W, 3) | (0.6H, 0.6W, 3) | Focus on eye |
| 4 | Resize | (0.6H, 0.6W, 3) | (224, 224, 3) | Match model input |
| 5 | Normalize | [0, 255] | [0.0, 1.0] | Stabilize inference |
| 6 | Expand Dims | (224, 224, 3) | (1, 224, 224, 3) | Add batch dimension |

### Visual Example

```
Original Image (1000×800)
    ↓ Center Crop (60%)
Cropped Image (600×480) - focused on center
    ↓ Resize
Resized Image (224×224) - model input size
    ↓ Normalize
Normalized Image - pixel values between 0 and 1
    ↓ Expand Dims
Batch Image (1, 224, 224, 3) - ready for model
```

---

## Prediction

### Understanding Model Output

The model outputs a probability distribution over 4 classes:

```python
# Example output
preds = [0.9234, 0.0421, 0.0234, 0.0111]
#          healthy   conjunctivitis  cataract  keratitis

# Interpretation:
# - 92.34% chance: Healthy eye
# - 4.21% chance: Conjunctivitis
# - 2.34% chance: Cataract
# - 1.11% chance: Keratitis

# Prediction: "healthy_eye" with 92.34% confidence
```

### Confidence Thresholds

| Confidence | Interpretation | Action |
|------------|----------------|--------|
| > 90% | High confidence | Trust prediction |
| 70-90% | Moderate confidence | Consider prediction, verify clinically |
| < 70% | Low confidence | Recommend specialist consultation |

### Class Mapping

```python
CLASS_NAMES = (
    "healthy_eye",                    # Index 0
    "Conjunctivitis Recognition",     # Index 1
    "Cataract dataset",               # Index 2
    "keratitis",                      # Index 3
)
```

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
  "confidence": 0.9234
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

1. **Model**: MobileNetV2-based CNN, optimized for speed and accuracy
2. **Input**: 224×224 RGB images, center-cropped and normalized
3. **Output**: 4-class classification with confidence scores
4. **Performance**: ~1 second inference time, singleton pattern for efficiency
5. **Deployment**: Hugging Face Hub for model distribution
6. **Safety**: Always validate predictions clinically

---

*For questions about the AI system, contact the AI/ML team lead.*

*Last Updated: April 29, 2026*  
*Document Version: 1.0*