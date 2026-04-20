"""
SQLAlchemy ORM models.
Every prediction + analysis is stored here for audit trail + monitoring.
"""

from sqlalchemy import Column, String, Float, DateTime, JSON, Text
from sqlalchemy.sql import func
from app.database.connection import Base


class PredictionLog(Base):
    __tablename__ = "prediction_logs"

    id = Column(String, primary_key=True)           # UUID
    transaction_id = Column(String, nullable=False, index=True)
    amount = Column(Float, nullable=False)
    fraud_probability = Column(Float, nullable=False)
    label = Column(String, nullable=False)          # FRAUD | LEGITIMATE
    risk_tier = Column(String, nullable=False)      # LOW | MEDIUM | HIGH
    recommended_action = Column(String, nullable=True)
    explanation = Column(Text, nullable=True)
    top_features = Column(JSON, nullable=True)      # list of dicts
    shap_values = Column(JSON, nullable=True)       # list of floats
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return (
            f"<PredictionLog id={self.id} "
            f"label={self.label} "
            f"prob={self.fraud_probability:.4f}>"
        )