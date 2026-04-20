from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import sys

from app.core.config import settings
from app.ml.predict import load_predictor
from app.routes.predict import router as predict_router
from app.routes.analyze import router as analyze_router
from app.database.connection import create_tables

logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | <cyan>{name}</cyan> — {message}",
    level="DEBUG" if settings.DEBUG else "INFO",
    colorize=True,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.APP_NAME} [{settings.ENVIRONMENT}]")
    await create_tables()
    load_predictor()
    logger.info("Application ready ✓")
    yield
    logger.info("Shutting down")


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else ["https://fraud-sentinel.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(predict_router)
app.include_router(analyze_router)


@app.get("/health", tags=["Health"])
async def health() -> dict:
    return {"status": "ok", "app": settings.APP_NAME}