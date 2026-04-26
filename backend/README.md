# Digital Ophthalmology Assistant - Backend API

FastAPI-based backend for AI-powered anterior eye disease classification.

## Features

- **ML Inference**: MobileNetV2-based eye disease classification
- **RESTful API**: Full CRUD operations for predictions, content, and library
- **Database**: SQLite (dev) / PostgreSQL (prod) with SQLAlchemy ORM
- **Image Upload**: Secure file upload with validation
- **CORS Support**: Configurable cross-origin requests

## Quick Start

### Prerequisites

- Python 3.11+
- pip or poetry

### Installation

```bash
# Clone repository
git clone <repo-url>
cd digital-ophthalmology-assistant/backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env with your configuration (optional)
```

### Running the Server

```bash
# Development mode (with auto-reload)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Server**: http://127.0.0.1:8000  
**API Docs**: http://127.0.0.1:8000/docs  
**ReDoc**: http://127.0.0.1:8000/redoc

## Docker Deployment

```bash
# Build image
docker build -t ophthalmology-api .

# Run container
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/models:/app/models \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/predictions.db:/app/predictions.db \
  ophthalmology-api
```

## API Endpoints

### Health & Info
- `GET /` - API information
- `GET /health` - Health check

### Prediction
- `POST /predict` - Upload image and get prediction

### Results
- `GET /api/v1/results` - List all predictions (with filters)
- `GET /api/v1/results/{id}` - Get specific prediction
- `DELETE /api/v1/results/{id}` - Delete prediction

### Content Management
- `GET /api/v1/content` - List content sections
- `GET /api/v1/content/{type}` - Get section by type
- `POST /api/v1/content` - Create content section
- `PUT /api/v1/content/{id}` - Update content section
- `DELETE /api/v1/content/{id}` - Delete content section

### Disease Library
- `GET /api/v1/library` - List diseases (with search/filters)
- `GET /api/v1/library/{id}` - Get disease details
- `POST /api/v1/library` - Add disease to library
- `PUT /api/v1/library/{id}` - Update disease
- `DELETE /api/v1/library/{id}` - Remove disease

### Questions
- `GET /api/v1/questions` - List questions
- `POST /api/v1/questions` - Create question
- `PUT /api/v1/questions/{id}` - Update question
- `DELETE /api/v1/questions/{id}` - Delete question

## Configuration

Copy `.env.example` to `.env` and configure:

| Variable | Description | Default |
|----------|-------------|---------|
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8000` |
| `DEBUG` | Debug mode | `false` |
| `DATABASE_URL` | Database connection string | SQLite at `predictions.db` |
| `MODEL_PATH` | Path to ML model | `models/eye_disease_final_cropped.keras` |
| `UPLOAD_DIR` | Upload directory | `uploads/` |
| `MAX_UPLOAD_SIZE_MB` | Max file size | `10` |

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI application
│   ├── config.py         # Configuration management
│   ├── database/
│   │   ├── __init__.py
│   │   └── db.py         # Database setup
│   ├── models/
│   │   ├── __init__.py
│   │   ├── prediction.py # Prediction model
│   │   ├── library_item.py
│   │   ├── question.py
│   │   └── section.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── predict.py    # Prediction endpoint
│   │   ├── results.py    # Results endpoints
│   │   ├── content.py    # Content management
│   │   ├── library.py    # Disease library
│   │   └── questions.py  # Questions CRUD
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ai_service.py # ML inference
│   │   └── seed_service.py # Initial data
│   └── uploads/          # Uploaded images
├── models/               # ML model files (not in repo)
├── requirements.txt
├── Dockerfile
└── .env.example
```

## ML Model

The backend uses a MobileNetV2-based model for classifying anterior eye diseases:

- **Input**: 224x224 RGB images
- **Classes**: healthy_eye, conjunctivitis, cataract, keratitis
- **Preprocessing**: Center crop (60%), resize, MobileNetV2 normalization

Place your trained model at:
```
backend/models/eye_disease_final_cropped.keras
```

## Production Deployment

### Using Gunicorn (Linux)

```bash
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120
```

### Using Render/Railway

1. Set build command: `pip install -r requirements.txt`
2. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. Add environment variables from `.env.example`
4. Upload model file separately or use a storage service

### Environment Variables for Production

```bash
# Database (PostgreSQL recommended)
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# CORS (restrict to your frontend domain)
CORS_ORIGINS=["https://yourdomain.com"]

# Disable debug
DEBUG=false
```

## Development

```bash
# Install dev dependencies (optional)
pip install pytest pytest-asyncio httpx black ruff mypy

# Run tests
pytest

# Format code
black app/

# Lint
ruff check app/

# Type check
mypy app/
```

## License

Proprietary - Delta University for Science and Technology