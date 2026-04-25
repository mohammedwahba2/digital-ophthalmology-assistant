from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.database.db import Base, engine
from app.database.db import SessionLocal
from app.models import library_item as _library_item_model  # noqa: F401
from app.models import prediction as _prediction_model  # noqa: F401
from app.models import question as _question_model  # noqa: F401
from app.models import section as _section_model  # noqa: F401
from app.routes.content import router as content_router
from app.routes.library import router as library_router
from app.routes.predict import router as predict_router
from app.routes.questions import router as questions_router
from app.routes.results import router as results_router
from app.services.seed_service import seed_content

app = FastAPI(title="Prediction Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_content(db)
    finally:
        db.close()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def root():
    return {"message": "Backend server is running"}


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(Exception)
async def unhandled_exception_handler(_: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


app.include_router(predict_router)
app.include_router(results_router)
app.include_router(questions_router)
app.include_router(content_router)
app.include_router(library_router)
