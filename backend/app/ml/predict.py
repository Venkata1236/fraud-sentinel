"""
Inference pipeline — loads model once at startup, serves every request.

Design decisions:
  - Singleton pattern: _predictor is module-level, loaded once.
  - load_predictor() called in FastAPI lifespan, not per-request.
  - get_predictor() called in route handler — returns cached instance.
"""

import json
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from loguru import logger

from app.core.config import settings
from app.ml.explainer import FraudExplainer
from app.models.schemas import PredictResponse, TopFeature

# Risk tier thresholds
LOW_THRESHOLD = 0.30
HIGH_THRESHOLD = 0.70

# Module-level singleton
_predictor: "FraudPredictor | None" = None


class FraudPredictor:
    def __init__(self):
        logger.info(f"Loading model from {settings.MODEL_PATH}")
        if not settings.MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Model file not found: {settings.MODEL_PATH}\n"
                "Run backend/notebooks/eda_training.ipynb first."
            )

        self.model = joblib.load(settings.MODEL_PATH)

        logger.info(f"Loading feature names from {settings.FEATURE_NAMES_PATH}")
        with open(settings.FEATURE_NAMES_PATH) as f:
            self.feature_names: list[str] = json.load(f)

        logger.info(f"Feature count: {len(self.feature_names)}")

        self.explainer = FraudExplainer(self.model, self.feature_names)
        logger.info("FraudPredictor ready ✓")

    def predict(self, features: list[float]) -> PredictResponse:
        """
        Single-transaction inference.
        Returns label, probabilities, risk tier, SHAP explanation.
        """
        X = pd.DataFrame([features], columns=self.feature_names)

        # model.predict_proba returns [[P(legit), P(fraud)]]
        proba = self.model.predict_proba(X)[0]
        fraud_prob = float(proba[1])
        confidence = float(max(proba))  # confidence in whichever label wins

        label = "FRAUD" if fraud_prob >= 0.5 else "LEGITIMATE"
        risk_tier = self._get_risk_tier(fraud_prob)

        explanation = self.explainer.explain(features)

        top_features = [
            TopFeature(**f) for f in explanation["top_features"]
        ]

        return PredictResponse(
            label=label,
            confidence=confidence,
            fraud_probability=fraud_prob,
            risk_tier=risk_tier,
            shap_values=explanation["shap_values"],
            top_features=top_features,
        )

    @staticmethod
    def _get_risk_tier(fraud_prob: float) -> str:
        if fraud_prob < LOW_THRESHOLD:
            return "LOW"
        elif fraud_prob < HIGH_THRESHOLD:
            return "MEDIUM"
        return "HIGH"


def load_predictor() -> None:
    """Called once during FastAPI startup lifespan."""
    global _predictor
    _predictor = FraudPredictor()


def get_predictor() -> FraudPredictor:
    """Dependency injection — returns singleton, raises if not loaded."""
    if _predictor is None:
        raise RuntimeError(
            "Predictor not loaded. "
            "Ensure load_predictor() is called in the FastAPI lifespan."
        )
    return _predictor   
# end of predict

# risk tier: LOW < 0.30, MEDIUM 0.30-0.70, HIGH > 0.70

# get_predictor() used as FastAPI Depends() injection
