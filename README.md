# Digital Ophthalmology Assistant

This project uses one eye disease classification pipeline across training and backend inference:

- Architecture: `MobileNetV2`
- Model file: `backend/models/eye_disease_final_cropped.h5`
- Dataset path: `backend/data/eye_dataset/`

## 1. Add Dataset

Place the dataset in this structure:

```text
backend/data/eye_dataset/
  healthy_eye/
  Conjunctivitis Recognition/
  Cataract dataset/
  keratitis/
```

## 2. Run Training

```bash
pip install -r backend/requirements-training.txt
python backend/train_model.py
```

The trained model will be saved to:

```text
backend/models/eye_disease_final_cropped.h5
```

## 3. Start Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend URLs:

- `http://127.0.0.1:8000`
- `http://127.0.0.1:8000/docs`
