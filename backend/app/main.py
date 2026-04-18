"""
FraudSentinel FastAPI application.

Lifespan pattern (FastAPI 0.95+):
  - Replaces deprecated @app.on_event("startup").
  - Model loads ONCE at startup, lives for entire process lifetime.
  - On shutdown, any cleanup (DB connection pool close) goes here.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import sys

from app.core.config import settings
from app.ml.predict import load_predictor
from app.routes.predict import router as predict_router

# ─── Loguru config ────────────────────────────────────────────────────────────
logger.remove()  # remove default handler
logger.add(
    sys.stdout,
    format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | <cyan>{name}</cyan> — {message}",
    level="DEBUG" if settings.DEBUG else "INFO",
    colorize=True,
)


# ─── Lifespan ─────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP
    logger.info(f"Starting {settings.APP_NAME} [{settings.ENVIRONMENT}]")
    load_predictor()   # loads XGBoost model + SHAP explainer into memory
    logger.info("Application ready ✓")
    yield
    # SHUTDOWN
    logger.info("Shutting down — releasing resources")


# ─── App factory ──────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "Real-time fraud detection API. "
        "Scores transactions with XGBoost, "
        "explains decisions with SHAP, "
        "routes investigations with LangGraph."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ─── CORS ─────────────────────────────────────────────────────────────────────
# Dev: allow all. Prod: replace with ["https://fraud-sentinel.vercel.app"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else ["https://fraud-sentinel.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routers ──────────────────────────────────────────────────────────────────
app.include_router(predict_router)
# app.include_router(analyze_router)  ← uncomment Day 2

# ─── Root health ──────────────────────────────────────────────────────────────
@app.get("/health", tags=["Health"])
async def health() -> dict:
    return {"status": "ok", "app": settings.APP_NAME, "env": settings.ENVIRONMENT}