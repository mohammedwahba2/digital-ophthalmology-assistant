# Backend API Technical Guide

##  Overview

This document provides a comprehensive guide to the FastAPI backend, including all endpoints, data models, and implementation details.

### Recent Improvements (v1.1)

The following enhancements have been implemented to improve reliability, scalability, and alignment with the project methodology:

1. **Standardized Disease Class Names**: All disease labels are now consistently formatted (lowercase with underscores: `healthy_eye`, `conjunctivitis`, `cataract`, `keratitis`).

2. **Enhanced Center Crop Algorithm**: The preprocessing pipeline now implements a proper center-crop algorithm that isolates the cornea and lens region, eliminating peripheral noise (eyelashes, skin, lighting artifacts) as described in the project methodology.

3. **Request ID Tracking**: Every request now receives a unique UUID for end-to-end tracing, logged in request headers (`X-Request-ID`) for debugging and monitoring.

4. **Pagination Support**: The `/api/v1/results` endpoint now supports pagination with configurable page size (default 20, max 100) to handle large datasets efficiently.

5. **Enhanced Error Handling**: Improved validation including image dimension constraints (min 50×50, max 4096×4096 pixels) and more descriptive error messages.

6. **Comprehensive Test Suite**: Added pytest-based tests covering prediction validation, AI service functionality, and the Center Crop algorithm.

7. **Production-Ready Docker**: Multi-stage build with non-root user, health checks, and optimized image size.

---

##  Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Project Structure](#project-structure)
3. [API Endpoints Reference](#api-endpoints-reference)
4. [Database Models](#database-models)
5. [Configuration](#configuration)
6. [Error Handling](#error-handling)
7. [Best Practices](#best-practices)

---

## Architecture Overview

### Technology Stack

| Component | Technology | Version |
|-----------|------------|---------|
| **Framework** | FastAPI | >=0.109.0 |
| **Language** | Python | 3.11+ |
| **Database ORM** | SQLAlchemy | >=2.0.25 |
| **Database** | SQLite (dev) / PostgreSQL (prod) | - |
| **Validation** | Pydantic | >=2.5.0 |
| **AI/ML** | TensorFlow | >=2.15.0 |
| **Image Processing** | Pillow | >=10.2.0 |
| **Model Hub** | Hugging Face Hub | >=0.20.0 |

### Application Flow

```
Request → Middleware → Router → Service → Database/AI → Response
```

### Key Design Patterns

1. **Dependency Injection**: FastAPI's Depends() for database sessions
2. **Repository Pattern**: Services abstract database operations
3. **Singleton Pattern**: AI model loaded once
4. **Context Managers**: Proper resource cleanup

---

## Project Structure

```
backend/
├── app/
│   ├── __init__.py              # Package initialization
│   ├── main.py                  # Application entry point
│   ├── config.py                # Configuration management
│   │
│   ├──  database/
│   │   ├── __init__.py
│   │   └── db.py                # Database connection & session
│   │
│   ├──  models/               # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── prediction.py        # Prediction records
│   │   ├── library_item.py      # Disease library
│   │   ├── section.py           # Content sections
│   │   └── question.py          # FAQ items
│   │
│   ├──  routes/               # API endpoints
│   │   ├── __init__.py
│   │   ├── predict.py           # POST /predict
│   │   ├── results.py           # GET/DELETE /api/v1/results
│   │   ├── library.py           # GET /api/v1/library
│   │   ├── content.py           # GET /api/v1/content
│   │   └── questions.py         # GET /api/v1/questions
│   │
│   └──  services/             # Business logic
│       ├── __init__.py
│       ├── ai_service.py        # AI inference
│       └── seed_service.py      # Database seeding
│
├── requirements.txt             # Python dependencies
├── .env.example                # Environment template
└── Dockerfile                  # Container configuration
```

---

## API Endpoints Reference

### Base URL

```
Development: http://localhost:8000
Production: http://your-domain.com
```

### API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

---

### 1. Health Check

**Endpoint:** `GET /health`

**Description:** Check if the API is running and healthy.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

**Status Codes:**
- `200 OK`: API is healthy
- `500 Internal Server Error`: API is unhealthy

---

### 2. Root Endpoint

**Endpoint:** `GET /`

**Description:** Get API information and available documentation.

**Response:**
```json
{
  "name": "Digital Ophthalmology Assistant",
  "version": "1.0.0",
  "docs": "/docs",
  "health": "/health"
}
```

---

### 3. Predict Eye Disease

**Endpoint:** `POST /predict`

**Description:** Upload an eye image and get AI-powered disease classification. The system uses a custom Center Crop preprocessing algorithm to isolate the ocular region before inference.

**Request:**
- **Content-Type:** `multipart/form-data`
- **Body:** 
  - `file` (binary): Image file (JPG, PNG, BMP, WebP)
  - Max size: 10 MB
  - Image dimensions: Min 50×50px, Max 4096×4096px

**Success Response (200):**
```json
{
  "label": "healthy_eye",
  "confidence": 0.9234
}
```

**Valid Prediction Labels:**
- `healthy_eye` - Normal eye without abnormalities
- `conjunctivitis` - Inflammation of the conjunctiva
- `cataract` - Lens opacification
- `keratitis` - Corneal inflammation

**Error Responses:**

| Code | Reason | Response |
|------|--------|----------|
| `400` | Missing filename | `{"detail": "Missing filename in upload"}` |
| `400` | Empty file | `{"detail": "Empty file received"}` |
| `400` | Image too small | `{"detail": "Image dimensions too small..."}` |
| `400` | Image too large | `{"detail": "Image dimensions too large..."}` |
| `413` | File too large | `{"detail": "File too large"}` |
| `415` | Unsupported type | `{"detail": "Unsupported file type: .gif"}` |
| `500` | Model not found | `{"detail": "Model not found. Please ensure the model is properly deployed."}` |
| `500` | Prediction failed | `{"detail": "Prediction failed due to an internal error"}` |

**Implementation:**
```python
# backend/app/routes/predict.py
@router.post("/predict", response_model=dict[str, str | float])
async def run_prediction(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> dict[str, str | float]:
    # 1. Validate file
    # 2. Validate image content
    # 3. Save file to upload directory
    # 4. Run AI prediction
    # 5. Save to database
    # 6. Return result
```

---

### 4. List Prediction Results

**Endpoint:** `GET /api/v1/results`

**Description:** Retrieve prediction records with optional filtering and pagination.

**Query Parameters:**
- `min_confidence` (optional): Filter by minimum confidence score (0.0-1.0)
- `prediction` (optional): Filter by prediction label
- `date_from` (optional): Filter by start date (ISO 8601 format)
- `date_to` (optional): Filter by end date (ISO 8601 format)
- `page` (optional): Page number, 1-indexed (default: 1)
- `page_size` (optional): Results per page (default: 20, max: 100)

**Success Response (200):**
```json
{
  "data": [
    {
      "id": 1,
      "image_path": "/path/to/uploads/uuid.jpg",
      "prediction": "healthy_eye",
      "confidence": 0.9234,
      "created_at": "2024-01-15T10:30:00"
    },
    {
      "id": 2,
      "image_path": "/path/to/uploads/uuid2.jpg",
      "prediction": "cataract",
      "confidence": 0.8756,
      "created_at": "2024-01-15T11:45:00"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_count": 150,
    "total_pages": 8,
    "has_next": true,
    "has_previous": false
  }
}
```

**Implementation:**
```python
# backend/app/routes/results.py
@router.get("/results")
def list_results(
    min_confidence: Optional[float] = Query(default=None, ge=0.0, le=1.0),
    prediction: Optional[str] = Query(default=None),
    date_from: Optional[datetime] = Query(default=None),
    date_to: Optional[datetime] = Query(default=None),
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(default=20, ge=1, le=100, description="Results per page"),
    db: Session = Depends(get_db),
):
    """List prediction results with pagination support."""
    query = db.query(Prediction)

    if min_confidence is not None:
        query = query.filter(Prediction.confidence >= min_confidence)
    if prediction is not None and prediction.strip():
        query = query.filter(Prediction.prediction == prediction.strip())
    if date_from is not None:
        query = query.filter(Prediction.created_at >= date_from)
    if date_to is not None:
        query = query.filter(Prediction.created_at <= date_to)

    total_count = query.count()
    offset = (page - 1) * page_size
    records = query.order_by(Prediction.created_at.desc()).offset(offset).limit(page_size).all()
    
    return {
        "data": [...],
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_count": total_count,
            "total_pages": (total_count + page_size - 1) // page_size,
            "has_next": offset + page_size < total_count,
            "has_previous": page > 1,
        }
    }
```

---

### 5. Get Single Result

**Endpoint:** `GET /api/v1/results/{result_id}`

**Description:** Retrieve a specific prediction by ID.

**Path Parameters:**
- `result_id` (integer): Prediction record ID

**Success Response (200):**
```json
{
  "id": 1,
  "image_path": "/path/to/uploads/uuid.jpg",
  "prediction": "healthy_eye",
  "confidence": 0.9234,
  "created_at": "2024-01-15T10:30:00"
}
```

**Error Responses:**
- `404 Not Found`: Result with ID not found

---

### 6. Delete Result

**Endpoint:** `DELETE /api/v1/results/{result_id}`

**Description:** Delete a specific prediction record.

**Path Parameters:**
- `result_id` (integer): Prediction record ID

**Success Response (200):**
```json
{
  "message": "Result deleted successfully"
}
```

**Error Responses:**
- `404 Not Found`: Result with ID not found

---

### 7. List Disease Library

**Endpoint:** `GET /api/v1/library`

**Description:** Retrieve disease information with search and filter capabilities.

**Query Parameters:**
- `q` (optional): Search term (searches in name and symptoms)
- `name` (optional): Filter by specific disease name

**Success Response (200):**
```json
[
  {
    "id": "healthy_eye",
    "name": "Healthy Eye",
    "name_ar": "عين سليمة",
    "short": "Normal eye without any detected abnormalities.",
    "short_ar": "عين طبيعية بدون أي تشوهات مكتشفة.",
    "symptoms_ar": ["رؤية واضحة", "لا يوجد احمرار", "لا يوجد ألم"],
    "red_flags_ar": ["تغير مفاجئ في الرؤية", "ألم شديد"],
    "safe_tips_ar": ["فحص دوري", "حماية من الأشعة فوق البنفسجية"],
    "when_to_see_doctor_ar": "سنوياً للفحص الدوري",
    "risk_level": "Low",
    "created_at": "2024-01-15T09:00:00",
    "updated_at": "2024-01-15T09:00:00"
  }
]
```

---

### 8. Get Disease Details

**Endpoint:** `GET /api/v1/library/{disease_id}`

**Description:** Get detailed information about a specific disease.

**Path Parameters:**
- `disease_id` (string): Disease identifier

**Success Response (200):**
```json
{
  "id": "cataract",
  "name": "Cataract",
  "name_ar": "المياه البيضاء",
  "short": "Clouding of the eye's lens...",
  "short_ar": "تعكر في عدسة العين...",
  "symptoms_ar": ["رؤية ضبابية", "حساسية للضوء", "رؤية هالات"],
  "red_flags_ar": ["فقدان البصر المفاجئ"],
  "safe_tips_ar": ["جراحة إزالة المياه البيضاء"],
  "when_to_see_doctor_ar": "فوراً عند ملاحظة أي تغير في الرؤية",
  "risk_level": "Moderate"
}
```

---

### 9. Get Content Section

**Endpoint:** `GET /api/v1/content/{section_type}`

**Description:** Retrieve educational content for specific sections.

**Path Parameters:**
- `section_type` (string): Section type (about, safety, education)

**Success Response (200):**
```json
{
  "title": "Safety Information",
  "content": {
    "intro": "Important safety guidelines...",
    "cards": [
      {
        "title": "Clinical Validation",
        "content": "Always validate AI predictions..."
      }
    ],
    "escalation_advice": "When to seek immediate medical attention..."
  }
}
```

---

### 10. Get Questions/FAQ

**Endpoint:** `GET /api/v1/questions`

**Description:** Retrieve frequently asked questions.

**Success Response (200):**
```json
[
  {
    "id": 1,
    "question": "How accurate is the AI?",
    "answer": "The AI model has been trained on...",
    "category": "technical"
  }
]
```

---

## Database Models

### 1. Prediction Model

**Table:** `predictions`

**Purpose:** Store AI prediction records for history tracking.

```python
class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    image_path = Column(String, nullable=False)
    prediction = Column(String, nullable=True)
    confidence = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
```

**Fields:**
- `id`: Unique identifier (auto-increment)
- `image_path`: Path to uploaded image file
- `prediction`: Disease label predicted by AI
- `confidence`: Confidence score (0.0 to 1.0)
- `created_at`: Timestamp of prediction

---

### 2. Library Item Model

**Table:** `library_items`

**Purpose:** Store disease information for the library section.

```python
class LibraryItem(Base):
    __tablename__ = "library_items"

    id = Column(Integer, primary_key=True, index=True)
    disease_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    name_ar = Column(String, nullable=False)
    short = Column(Text, nullable=False)
    short_ar = Column(Text, nullable=False)
    symptoms_ar = Column(Text, nullable=False)  # JSON array
    red_flags_ar = Column(Text, nullable=False)  # JSON array
    safe_tips_ar = Column(Text, nullable=False)  # JSON array
    when_to_see_doctor_ar = Column(Text, nullable=False)
    risk_level = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
```

**Fields:**
- `disease_id`: Unique identifier (e.g., "cataract", "healthy_eye")
- `name`: English disease name
- `name_ar`: Arabic disease name
- `short`: Short English description
- `short_ar`: Short Arabic description
- `symptoms_ar`: JSON array of symptoms in Arabic
- `red_flags_ar`: JSON array of warning signs in Arabic
- `safe_tips_ar`: JSON array of safe tips in Arabic
- `when_to_see_doctor_ar`: When to consult a doctor (Arabic)
- `risk_level`: Low, Moderate, or High

---

### 3. Section Model

**Table:** `sections`

**Purpose:** Store educational content sections (about, safety, education).

```python
class Section(Base):
    __tablename__ = "sections"

    id = Column(Integer, primary_key=True, index=True)
    section_type = Column(String, unique=True, nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)  # JSON
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
```

---

### 4. Question Model

**Table:** `questions`

**Purpose:** Store FAQ items.

```python
class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(String, nullable=False)
    answer = Column(Text, nullable=False)
    category = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
```

---

## Configuration

### Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# Server
HOST=0.0.0.0
PORT=8000

# Application
DEBUG=false
APP_NAME="Digital Ophthalmology Assistant"
APP_VERSION=1.0.0

# Database
DATABASE_URL=sqlite:///./predictions.db

# CORS
CORS_ORIGINS=["*"]

# DL Model
MODEL_PATH=

# File Upload
UPLOAD_DIR=
MAX_UPLOAD_SIZE_MB=10
```

### Configuration Class

```python
# backend/app/config.py
class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    app_name: str = "Digital Ophthalmology Assistant"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Server
    host: str = "0.0.0.0"
    port: int = 7860
    
    # Database
    database_url: str | None = None
    
    # CORS
    cors_origins: list[str] = ["*"]
    
    # DL Model
    model_repo_id: str = "mohamed-wahba77/eye-disease-model"
    model_filename: str = "model.keras"
    
    # File Upload
    upload_dir: Path | None = None
    max_upload_size_mb: int = 10
    allowed_extensions: set[str] = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
```

---

### Request ID Tracking

Every request is assigned a unique UUID that is:
- Logged at the start and end of each request
- Included in the response header `X-Request-ID`
- Used for end-to-end request tracing in production

**Example Request/Response:**
```
Request Header:  (auto-generated)
Response Header: X-Request-ID: 550e8400-e29b-41d4-a716-446655440000
```

---

## Error Handling

### Custom Exception Handlers

```python
# backend/app/main.py

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with consistent format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "status_code": exc.status_code},
    )

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Handle unhandled exceptions with logging."""
    logger.error(f"Unhandled exception in {request.method} {request.url}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "status_code": 500},
    )
```

### Standard Error Response Format

```json
{
  "detail": "Error message describing what went wrong",
  "status_code": 400
}
```

### Common HTTP Status Codes

| Code | Meaning | Usage |
|------|---------|-------|
| `200` | OK | Successful request |
| `400` | Bad Request | Invalid input (missing file, empty file) |
| `404` | Not Found | Resource not found (result ID, disease ID) |
| `413` | Payload Too Large | File exceeds size limit |
| `415` | Unsupported Media Type | Invalid file extension |
| `500` | Internal Server Error | Server-side error (model loading, prediction) |

---

## AI Service Implementation

### Center Crop Algorithm

The custom Center Crop algorithm is a key component of the preprocessing pipeline, as described in the project methodology. It isolates the cornea and lens region by cropping the central 60% of the image, effectively eliminating peripheral noise.

```python
# backend/app/services/ai_service.py

def _center_crop(img: Image.Image, crop_ratio: float = 0.6) -> Image.Image:
    """Custom Center Crop Algorithm for Ocular Focus.
    
    This algorithm isolates the cornea and lens region by cropping the central 
    portion of the image, effectively eliminating non-pathological noise such 
    as eyelashes, skin, and lighting artifacts from the periphery.
    """
    w, h = img.size
    
    # Calculate crop boundaries to center on the ocular region
    left = w * (1 - crop_ratio) / 2
    top = h * (1 - crop_ratio) / 2
    right = w * (1 + crop_ratio) / 2
    bottom = h * (1 + crop_ratio) / 2
    
    return img.crop((left, top, right, bottom))
```

### Disease Classification Labels

All disease labels follow a consistent naming convention (lowercase with underscores):

```python
CLASS_NAMES = (
    "healthy_eye",      # Normal eye
    "conjunctivitis",   # Inflammation of conjunctiva
    "cataract",         # Lens opacification
    "keratitis",        # Corneal inflammation
)
```

---

## Testing

### Running Tests

```bash
cd backend
pip install pytest pillow
pytest tests/ -v
```

### Test Coverage

| Module | Tests | Coverage |
|--------|-------|----------|
| `test_predict.py` | Image validation, format support, dimension constraints | Prediction endpoint |
| `test_ai_service.py` | Center Crop algorithm, class names | AI service |

### Example Test

```python
# backend/tests/test_ai_service.py
class TestCenterCropAlgorithm:
    """Tests for the custom Center Crop preprocessing algorithm."""
    
    def test_center_crop_preserves_aspect_ratio(self):
        """Test that center crop maintains the original aspect ratio."""
        img = Image.new('RGB', (100, 100), color=(255, 0, 0))
        cropped = _center_crop(img)
        
        expected_size = int(100 * 0.6)
        assert abs(cropped.size[0] - expected_size) <= 1
        assert abs(cropped.size[1] - expected_size) <= 1
```

---

## Best Practices

### 1. Database Session Management

Always use dependency injection for database sessions:

```python
@router.get("/results")
async def list_results(db: Session = Depends(get_db)):
    # Database operations here
    pass  # Session automatically closed after request
```

### 2. Input Validation

Use Pydantic models for request/response validation:

```python
class PredictionSchema(BaseModel):
    label: str
    confidence: float

    class Config:
        json_schema_extra = {
            "example": {
                "label": "healthy_eye",
                "confidence": 0.9234
            }
        }
```

### 3. Error Handling

Always handle exceptions gracefully:

```python
try:
    label, confidence = predict_image(file_path)
except FileNotFoundError:
    raise HTTPException(
        status_code=500,
        detail="Model not found on HuggingFace Hub"
    )
except Exception:
    raise HTTPException(
        status_code=500,
        detail="Prediction failed"
    )
```

### 4. Logging

Use proper logging for debugging and monitoring:

```python
logger = logging.getLogger(__name__)

logger.info("Starting up Digital Ophthalmology Assistant...")
logger.warning(f"Failed to preload DL model: {e}")
logger.error(f"Unhandled exception: {exc}")
```

### 5. Type Hints

Always use type hints for better code clarity:

```python
def predict_image(image_path: str | Path) -> Tuple[str, float]:
    """Run inference on image and return prediction."""
    pass
```

### 6. Async/Await

Use async for I/O-bound operations:

```python
@router.post("/predict")
async def run_prediction(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    content = await file.read()  # Async file read
    # ...
```

---

## Testing the API

### Using curl

```bash
# Health check
curl http://localhost:8000/health

# Predict
curl -X POST http://localhost:8000/predict \
  -F "file=@/path/to/eye_image.jpg"

# List results
curl http://localhost:8000/api/v1/results

# Get disease library
curl http://localhost:8000/api/v1/library
```

### Using Python requests

```python
import requests

# Health check
response = requests.get("http://localhost:8000/health")
print(response.json())

# Predict
with open("eye_image.jpg", "rb") as f:
    files = {"file": f}
    response = requests.post("http://localhost:8000/predict", files=files)
    print(response.json())

# List results
response = requests.get("http://localhost:8000/api/v1/results")
print(response.json())
```

---

## Running the Backend

### Development Mode

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker

```bash
cd backend
docker build -t ophthalmology-api .
docker run -p 8000:8000 ophthalmology-api
```

---

*For questions about the backend, contact the Backend team lead.*

*Last Updated: April 29, 2026*  
*Document Version: 1.1*

---

## Changelog

### Version 1.1 (April 29, 2026)

- **Fixed**: Standardized disease class names (`conjunctivitis`, `cataract` instead of inconsistent names)
- **Improved**: Center Crop algorithm now properly centers on ocular region with configurable crop ratio
- **Added**: Request ID tracking middleware for end-to-end request tracing
- **Added**: Pagination support for `/api/v1/results` endpoint
- **Added**: Image dimension validation (min 50×50, max 4096×4096 pixels)
- **Improved**: Enhanced error handling with descriptive messages
- **Improved**: Production-ready Docker configuration with multi-stage build
- **Added**: Comprehensive test suite with pytest

### Version 1.0 (Initial Release)

- Initial implementation of FastAPI backend
- AI inference with TensorFlow/Keras model
- SQLite database with SQLAlchemy ORM
- CRUD operations for predictions, library items, content sections, and questions
