# Digital Ophthalmology Assistant - Backend API

FastAPI-based backend for AI-powered anterior eye disease classification.

> **Note**: This README provides complete step-by-step instructions to set up and run the project from scratch. **No Docker required** - everything runs natively with Python.

---

## 📋 Table of Contents

1. [Features](#features)
2. [Prerequisites](#prerequisites)
3. [Installation (Step by Step)](#installation-step-by-step)
4. [Running the Server](#running-the-server)
5. [API Documentation](#api-documentation)
6. [Configuration](#configuration)
7. [Project Structure](#project-structure)
8. [ML Model Setup](#ml-model-setup)
9. [Troubleshooting](#troubleshooting)

---

## ✨ Features

- **ML Inference**: Eye disease classification using deep learning
- **RESTful API**: Full CRUD operations for predictions, content, and library
- **Database**: SQLite (development) / PostgreSQL (production) with SQLAlchemy ORM
- **Image Upload**: Secure file upload with validation (size, format)
- **CORS Support**: Configurable cross-origin requests
- **Production Ready**: Logging, error handling, thread-safe ML inference

---

## 🛠 Prerequisites

Before you begin, ensure you have:

- **Python 3.11+** (download from [python.org](https://www.python.org/downloads/))
- **pip** (comes with Python)
- **Git** (for cloning the repository)

### Check your Python version:
```bash
python --version  # Should be 3.11 or higher
```

---

## 📦 Installation (Step by Step)

### Step 1: Clone the Repository

```bash
# Clone the repository
git clone <repository-url>

# Navigate to the backend directory
cd digital-ophthalmology-assistant/backend
```

### Step 2: Create Virtual Environment

```bash
# Create a virtual environment named .venv
python -m venv .venv
```

### Step 3: Activate Virtual Environment

**On macOS/Linux:**
```bash
source .venv/bin/activate
```

**On Windows (Command Prompt):**
```cmd
.venv\Scripts\activate
```

**On Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1
```

> You should see `(.venv)` at the beginning of your terminal prompt.

### Step 4: Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt
```

This will install:
- FastAPI
- Uvicorn (web server)
- SQLAlchemy (database ORM)
- Pydantic (data validation)
- TensorFlow CPU (ML inference)
- Pillow (image processing)
- NumPy (numerical operations)

### Step 5: Set Up Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# (Optional) Edit .env with your settings
# Most settings have sensible defaults
```

### Step 6: Add the ML Model

**Important**: The model file is NOT included in the repository. You need to add it:

1. Create the models directory if it doesn't exist:
   ```bash
   mkdir -p models
   ```

2. Place your trained model file at:
   ```
   backend/models/eye_disease_final_cropped.keras
   ```

3. Verify the model exists:
   ```bash
   ls -la models/
   ```

---

## 🚀 Running the Server

### Development Mode (with auto-reload)

```bash
# Make sure you're in the backend directory and .venv is activated
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
# With multiple workers for better performance
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Verify the Server is Running

Open your browser and visit:
- **API Root**: http://127.0.0.1:8000
- **API Docs (Swagger)**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc
- **Health Check**: http://127.0.0.1:8000/health

You should see a welcome message or the interactive API documentation.

---

## 📖 API Documentation

### Interactive Documentation

FastAPI provides automatic interactive documentation:

- **Swagger UI**: http://127.0.0.1:8000/docs
  - Interactive interface to test all endpoints
  - Shows request/response schemas
  - Allows you to try out API calls directly

- **ReDoc**: http://127.0.0.1:8000/redoc
  - Clean, readable documentation
  - Good for sharing with team members

### Key Endpoints

#### Health & Info
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API information |
| GET | `/health` | Health check |

#### Prediction
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/predict` | Upload image and get prediction |

#### Results (Prediction History)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/results` | List all predictions |
| GET | `/api/v1/results/{id}` | Get specific prediction |
| DELETE | `/api/v1/results/{id}` | Delete prediction |

#### Content Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/content` | List content sections |
| GET | `/api/v1/content/{type}` | Get section by type |
| POST | `/api/v1/content` | Create content section |
| PUT | `/api/v1/content/{id}` | Update content section |
| DELETE | `/api/v1/content/{id}` | Delete content section |

#### Disease Library
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/library` | List diseases (with search) |
| GET | `/api/v1/library/{id}` | Get disease details |
| POST | `/api/v1/library` | Add disease to library |
| PUT | `/api/v1/library/{id}` | Update disease |
| DELETE | `/api/v1/library/{id}` | Remove disease |

---

## ⚙️ Configuration

Copy `.env.example` to `.env` and configure as needed:

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `HOST` | Server host | `0.0.0.0` | `127.0.0.1` |
| `PORT` | Server port | `8000` | `8080` |
| `DEBUG` | Debug mode | `false` | `true` |
| `DATABASE_URL` | Database connection | SQLite | `postgresql://user:pass@localhost/db` |
| `MODEL_PATH` | Path to ML model | `models/eye_disease_final_cropped.keras` | `/custom/path/model.keras` |
| `UPLOAD_DIR` | Upload directory | `uploads/` | `/var/uploads` |
| `MAX_UPLOAD_SIZE_MB` | Max file size | `10` | `20` |
| `CORS_ORIGINS` | Allowed origins | `["*"]` | `["https://mydomain.com"]` |

---

## 📁 Project Structure

```
backend/
├── app/
│   ├── __init__.py           # Package initializer
│   ├── main.py               # FastAPI application entry point
│   ├── config.py             # Configuration management
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   └── db.py             # Database setup & session management
│   │
│   ├── models/               # SQLAlchemy database models
│   │   ├── __init__.py
│   │   ├── prediction.py     # Prediction record model
│   │   ├── library_item.py   # Disease library model
│   │   ├── question.py       # Questions model
│   │   └── section.py        # Content sections model
│   │
│   ├── routes/               # API endpoints
│   │   ├── __init__.py
│   │   ├── predict.py        # Prediction endpoint
│   │   ├── results.py        # Results CRUD endpoints
│   │   ├── content.py        # Content management endpoints
│   │   ├── library.py        # Disease library endpoints
│   │   └── questions.py      # Questions CRUD endpoints
│   │
│   ├── services/             # Business logic
│   │   ├── __init__.py
│   │   ├── ai_service.py     # ML inference service
│   │   └── seed_service.py   # Database seeding
│   │
│   └── uploads/              # Uploaded images (created automatically)
│
├── models/                   # ML model files (NOT in repo - add manually)
│   └── eye_disease_final_cropped.keras
│
├── .env.example              # Environment variables template
├── .gitignore                # Git exclusions
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

---

## 🧠 ML Model Setup

### Model Requirements

- **Format**: Keras (.keras or .h5)
- **Input Size**: 224×224 pixels
- **Input Type**: RGB images
- **Architecture**: MobileNetV2-based

### Preprocessing Pipeline

The model expects images preprocessed as follows:
1. Center crop (60% of original image)
2. Resize to 224×224
3. Normalize pixel values to [0, 1] (divide by 255)
4. Expand dimensions for batch inference

### Model Classes

The model classifies into 4 categories:
1. `healthy_eye` - Normal/healthy eye
2. `Conjunctivitis Recognition` - Conjunctivitis
3. `Cataract dataset` - Cataract
4. `keratitis` - Keratitis

### Adding Your Model

1. Create the models directory:
   ```bash
   mkdir -p models
   ```

2. Place your model file:
   ```bash
   cp /path/to/your/trained/model.keras models/eye_disease_final_cropped.keras
   ```

3. Verify the model exists:
   ```bash
   ls -la models/
   ```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. "ModuleNotFoundError: No module named 'fastapi'"
**Solution**: Make sure your virtual environment is activated:
```bash
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate     # Windows
```

#### 2. "Address already in use" error
**Solution**: Another process is using port 8000. Either:
- Kill the process using port 8000
- Use a different port: `uvicorn app.main:app --port 8001`

#### 3. "Model file not found"
**Solution**: Make sure the model file exists at:
```
backend/models/eye_disease_final_cropped.keras
```

#### 4. "Permission denied" when creating directories
**Solution**: Run with appropriate permissions or create directories manually:
```bash
mkdir -p models uploads
```

#### 5. TensorFlow import errors
**Solution**: Ensure you have the correct Python version (3.11) and try:
```bash
pip uninstall tensorflow tensorflow-cpu
pip install tensorflow-cpu==2.15.0
```

### Getting Help

If you encounter issues not listed here:

1. Check the logs (they appear in the terminal where you ran uvicorn)

2. Verify your environment:
   ```bash
   python --version
   pip list
   ```

3. Test the database:
   ```bash
   # The database is created automatically on first run
   # Check if predictions.db exists in backend/
   ls -la predictions.db
   ```

---

## 📄 License

Proprietary - Delta University for Science and Technology

---

## 👥 Credits

Developed by the AI-Based Eye Disease Classification Team at Delta University for Science and Technology.

**Supervisor**: Dr. Eman Salah  
**Team Members**: Fares Tamer, Israa Eldsouky, Mohamed Ayman, Mohamed Mahmoud, Karim Saeed, Rawan Elsaid, Ohoud Abdelnaem, Sama Abdeltawab, Waad Ahmed, Wesam Mohamed, Zeyad Waleed