from pydantic import BaseModel, Field, field_validator
from typing import Literal
from datetime import datetime


# ─── /predict ────────────────────────────────────────────────────────────────

class PredictRequest(BaseModel):
    """
    30 float features: Time, V1–V28, Amount
    Strict length validation — wrong length → 422 before touching the model.
    """
    features: list[float] = Field(
        ...,
        min_length=30,
        max_length=30,
        description="Exactly 30 floats: [Time, V1, V2, ..., V28, Amount]",
        examples=[[0.0] * 30],
    )

    @field_validator("features")
    @classmethod
    def validate_no_nan(cls, v: list[float]) -> list[float]:
        import math
        if any(math.isnan(x) or math.isinf(x) for x in v):
            raise ValueError("features must not contain NaN or Inf values")
        return v


class TopFeature(BaseModel):
    feature: str
    raw_value: float    # actual feature value in this transaction
    shap_impact: float  # SHAP contribution — positive = pushes toward FRAUD


class PredictResponse(BaseModel):
    label: Literal["FRAUD", "LEGITIMATE"]
    confidence: float = Field(..., ge=0.0, le=1.0)
    fraud_probability: float = Field(..., ge=0.0, le=1.0)
    risk_tier: Literal["LOW", "MEDIUM", "HIGH"]
    shap_values: list[float]          # one per feature (30 values)
    top_features: list[TopFeature]    # top 5 by absolute SHAP impact


# ─── /analyze (LangGraph — Day 2) ────────────────────────────────────────────

class AnalyzeRequest(BaseModel):
    """
    Wraps prediction output + transaction metadata for LangGraph routing.
    Amount + timestamp are human-readable context for the LLM explanation.
    """
    transaction_id: str = Field(..., description="UUID for this transaction")
    amount: float = Field(..., gt=0)
    timestamp: datetime
    features: list[float] = Field(..., min_length=30, max_length=30)
    # Pre-computed from /predict (optional — analyze will recompute if absent)
    fraud_probability: float | None = Field(default=None, ge=0.0, le=1.0)


class InvestigationReport(BaseModel):
    transaction_id: str
    risk_tier: Literal["LOW", "MEDIUM", "HIGH"]
    fraud_probability: float
    recommended_action: Literal["AUTO_APPROVE", "FLAG_FOR_REVIEW", "BLOCK_AND_ESCALATE"]
    explanation: str                  # plain-language LLM explanation
    top_features: list[TopFeature]
    escalation_reason: str | None     # None for LOW tier
    analyst_notes: str | None         # None for LOW tier


class AnalyzeResponse(BaseModel):
    status: Literal["completed", "error"]
    report: InvestigationReport | None
    error_message: str | None = None


# ─── DB record (PostgreSQL — Day 3) ──────────────────────────────────────────

class TransactionRecord(BaseModel):
    transaction_id: str
    amount: float
    fraud_probability: float
    label: Literal["FRAUD", "LEGITIMATE"]
    risk_tier: Literal["LOW", "MEDIUM", "HIGH"]
    recommended_action: str
    top_features: list[TopFeature]
    created_at: datetime

    class Config:
        from_attributes = True   # enables ORM mode for SQLAlchemy