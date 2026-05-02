# Digital Ophthalmology Assistant

AI-powered ophthalmology assistant for anterior eye disease classification using deep learning.

> **A project by the Faculty of Artificial Intelligence, Delta University for Science and Technology**

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Project Structure](#project-structure)
4. [Backend Setup](#backend-setup)
5. [Frontend Setup](#frontend-setup)
6. [API Documentation](#api-documentation)
7. [Model Information](#model-information)
8. [Team](#team)

---

## ✨ Overview

This project provides an AI-based classification system for anterior eye diseases using MobileNetV2 architecture. It includes:

- **Backend API**: FastAPI server with ML inference capabilities
- **Frontend**: Responsive web application with image upload and prediction display
- **Database**: SQLite (development) / PostgreSQL (production)
- **Disease Library**: Comprehensive information about eye diseases in English and Arabic

### Supported Conditions

| Condition | Arabic | Risk Level |
|-----------|--------|------------|
| Healthy Eye | طبيعي | Low |
| Conjunctivitis | التهاب الملتحمة | Moderate |
| Cataract | المياه البيضاء | Moderate |
| Pterygium | الظفرة | Moderate |
| Keratitis | التهاب القرنية | High |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- pip (comes with Python)
- Modern web browser

### Run Everything

**Terminal 1 - Start Backend:**
```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# macOS/Linux:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file (optional)
cp .env.example .env

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Start Frontend:**
```bash
# Navigate to frontend
cd frontend

# Start simple HTTP server
python -m http.server 8080
```

**Open Browser:**
- Frontend: http://127.0.0.1:8080/pages/index.html
- Backend API Docs: http://127.0.0.1:8000/docs

---

## 📁 Project Structure

```
digital-ophthalmology-assistant/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py             # FastAPI application
│   │   ├── config.py           # Configuration management
│   │   ├── database/           # Database setup
│   │   ├── models/             # SQLAlchemy models
│   │   ├── routes/             # API endpoints
│   │   └── services/           # Business logic (ML, seeding)
│   ├── models/                 # ML model files (add manually)
│   ├── uploads/                # Uploaded images
│   ├── requirements.txt        # Python dependencies
│   ├── .env.example           # Configuration template
│   ├── Dockerfile             # Docker configuration (optional)
│   └── README.md              # Backend documentation
│
├── frontend/                   # Static web frontend
│   ├── pages/                 # HTML pages
│   ├── styles/                # CSS styles
│   ├── js/                    # JavaScript (app.js)
│   ├── assets/                # Icons and assets
│   └── README.md              # Frontend documentation
│
├── .gitignore                 # Git exclusions
├── AUDIT_REPORT.md           # Detailed audit report
└── README.md                 # This file
```

---

## 🔧 Backend Setup

### Installation

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

### Configuration

Copy `.env.example` to `.env` and configure as needed:

| Variable | Description | Default |
|----------|-------------|---------|
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8000` |
| `DEBUG` | Debug mode | `false` |
| `DATABASE_URL` | Database connection | SQLite |
| `MODEL_PATH` | Path to ML model | `models/final_eye_model_optimized.h5` |
| `UPLOAD_DIR` | Upload directory | `uploads/` |
| `MAX_UPLOAD_SIZE_MB` | Max file size | `10` |

### Add ML Model

**Important**: The model file is NOT included in the repository. Place your trained model at:

```
backend/models/final_eye_model_optimized.h5
```

### Run Backend

```bash
# Development mode
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Backend URLs

- **API Root**: http://127.0.0.1:8000
- **API Docs (Swagger)**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc
- **Health Check**: http://127.0.0.1:8000/health

For detailed backend documentation, see [backend/README.md](backend/README.md).

---

## 🖥️ Frontend Setup

### Run Frontend

```bash
cd frontend
python -m http.server 8080
```

Open: http://127.0.0.1:8080/pages/index.html

### Configure API URL

If your backend is not on the default URL, set it via:

```javascript
// In browser console:
localStorage.setItem("doa-api-base", "http://your-backend-url:8000");
location.reload();
```

### Pages

| Page | Description |
|------|-------------|
| Home | Project overview and featured diseases |
| Diagnose | Upload eye image for AI analysis |
| Diseases | Searchable disease library |
| History | View and manage past predictions |
| About | Project information and team |
| Safety | Disclaimers and safety information |
| Education | Patient education and tips |

For detailed frontend documentation, see [frontend/README.md](frontend/README.md).

---

## 📖 API Documentation

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API information |
| GET | `/health` | Health check |
| POST | `/predict` | Upload image and get prediction |
| GET | `/api/v1/results` | List all predictions |
| GET | `/api/v1/results/{id}` | Get specific prediction |
| DELETE | `/api/v1/results/{id}` | Delete prediction |
| GET | `/api/v1/library` | List diseases (with search) |
| GET | `/api/v1/library/{id}` | Get disease details |
| GET | `/api/v1/content/{type}` | Get page content |

### Example: Predict Eye Disease

```bash
curl -X POST http://127.0.0.1:8000/predict \
  -F "file=@/path/to/eye_image.jpg"
```

Response:
```json
{
  "label": "healthy_eye",
  "confidence": 0.9523
}
```

---

## 🧠 Model Information

### Architecture

- **Model**: MobileNetV2-based CNN
- **Input Size**: 224×224 pixels
- **Input Type**: RGB images
- **Format**: Keras (.keras)

### Preprocessing

1. Center crop (60% of original image)
2. Resize to 224×224
3. Normalize pixel values to [0, 1] (divide by 255)
4. Expand dimensions for batch inference

### Classes

The model classifies into 4 categories:
1. `healthy_eye` - Normal/healthy eye
2. `Conjunctivitis Recognition` - Conjunctivitis
3. `Cataract dataset` - Cataract
4. `keratitis` - Keratitis

---

## 👥 Team

**Supervisor**: Dr. Eman Salah

**Team Members**:
- Fares Tamer Abdel Majeed - 4241097
- Israa Eldsouky Ibrahim - 4241107
- Mohamed Ayman Dorgham - 4241041
- Mohamed Mahmoud Wahba - 4241543
- Karim Saeed Ahmed - 4241153
- Rawan Elsaid Elrasef - 4241331
- Ohoud Abdelnaem Abdallah - 4241386
- Sama Abdeltawab Elshaikh - 4241400
- Waad Ahmed Gaffer - 4241415
- Wesam Mohamed Maylo - 42411018
- Zeyad Waleed Mohamed - 4232012

---

## 📄 Additional Documentation

- [Backend README](backend/README.md) - Detailed backend setup and API reference
- [Frontend README](frontend/README.md) - Frontend features and configuration
- [Audit Report](AUDIT_REPORT.md) - Complete production audit details

---

## ⚠️ Disclaimer

This platform is for **educational and demonstration purposes only**. The diagnostic output is generated by an AI model and should not replace professional medical advice, diagnosis, or treatment. Always seek the advice of a qualified ophthalmologist for any eye-related concerns.

---

## 📄 License

Proprietary - Delta University for Science and Technology