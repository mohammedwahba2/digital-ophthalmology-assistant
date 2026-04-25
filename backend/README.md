# FastAPI Backend (Inference Only)

## 1) Environment Setup

Requires Python 3.10+.

```bash
cd backend
python -m venv .venv
```

Activate the virtual environment, then install dependencies:

```bash
pip install -r requirements.txt
```

## 2) Run Server

```bash
uvicorn app.main:app --reload
```

Server: `http://127.0.0.1:8000`
Docs: `http://127.0.0.1:8000/docs`

## 3) Model Path

The backend loads a single inference model from:

```text
backend/models/eye_disease_final_cropped.keras
```

The model is loaded with `tf.keras.models.load_model()` in `app/services/ai_service.py`.

## 4) API Endpoints

- `GET /health`
- `POST /predict`
- `GET /api/v1/results/{id}`
- `GET /api/v1/results`
- `DELETE /api/v1/results/{id}`

## 5) Notes

- Preprocessing remains inference-only and uses center crop, resize to `224x224`, and MobileNetV2 `preprocess_input`.
- No dataset or training workflow is required by the backend.
