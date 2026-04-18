from pydantic_settings import BaseSettings
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # backend/


class Settings(BaseSettings):
    # App
    APP_NAME: str = "FraudSentinel API"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Model
    MODEL_PATH: Path = BASE_DIR / "models" / "fraud_model.pkl"
    FEATURE_NAMES_PATH: Path = BASE_DIR / "models" / "feature_names.json"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/fraudsentinel"

    # OpenAI (for LangGraph Day 2)
    OPENAI_API_KEY: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()