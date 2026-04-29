# Backend API Technical Guide

##  Overview

This document provides a comprehensive guide to the FastAPI backend, including all endpoints, data models, and implementation details.

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

**Description:** Upload an eye image and get AI-powered disease classification.

**Request:**
- **Content-Type:** `multipart/form-data`
- **Body:** 
  - `file` (binary): Image file (JPG, PNG, BMP, WebP)
  - Max size: 10 MB

**Success Response (200):**
```json
{
  "label": "healthy_eye",
  "confidence": 0.9234
}
```

**Error Responses:**

| Code | Reason | Response |
|------|--------|----------|
| `400` | Missing filename | `{"detail": "Missing filename in upload"}` |
| `400` | Empty file | `{"detail": "Empty file received"}` |
| `413` | File too large | `{"detail": "File too large"}` |
| `415` | Unsupported type | `{"detail": "Unsupported file type: .gif"}` |
| `500` | Model not found | `{"detail": "Model not found on HuggingFace Hub"}` |
| `500` | Prediction failed | `{"detail": "Prediction failed"}` |

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

**Description:** Retrieve all prediction records with optional filtering.

**Query Parameters:**
- `prediction` (optional): Filter by prediction label

**Success Response (200):**
```json
[
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
]
```

**Implementation:**
```python
# backend/app/routes/results.py
@router.get("/results", response_model=list[PredictionSchema])
async def list_results(
    prediction: str | None = None,
    db: Session = Depends(get_db)
):
    query = db.query(Prediction)
    if prediction:
        query = query.filter(Prediction.prediction == prediction)
    return query.order_by(Prediction.created_at.desc()).all()
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

*Last Updated: [Current Date]*  
*Document Version: 1.0*