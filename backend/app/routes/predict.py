from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger
import time
import uuid

from app.models.schemas import PredictRequest, PredictResponse
from app.ml.predict import get_predictor, FraudPredictor
from app.database.connection import get_db
from app.database.models import PredictionLog

router = APIRouter(prefix="/predict", tags=["Prediction"])


@router.post("", response_model=PredictResponse)
async def predict_transaction(
    request: PredictRequest,
    predictor: FraudPredictor = Depends(get_predictor),
    db: AsyncSession = Depends(get_db),
) -> PredictResponse:
    start = time.perf_counter()

    try:
        result = predictor.predict(request.features)
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction error: {str(e)}",
        )

    elapsed_ms = (time.perf_counter() - start) * 1000

    # Log to PostgreSQL
    try:
        log = PredictionLog(
            id=str(uuid.uuid4()),
            transaction_id=str(uuid.uuid4()),
            amount=request.features[-1],          # Amount is last feature
            fraud_probability=result.fraud_probability,
            label=result.label,
            risk_tier=result.risk_tier,
            top_features=[f.model_dump() for f in result.top_features],
            shap_values=result.shap_values,
        )
        db.add(log)
        await db.commit()
    except Exception as e:
        logger.warning(f"DB logging failed (non-fatal): {e}")
        await db.rollback()

    logger.info(
        f"Predicted | label={result.label} | "
        f"fraud_prob={result.fraud_probability:.4f} | "
        f"risk={result.risk_tier} | "
        f"latency={elapsed_ms:.2f}ms"
    )

    return result


@router.get("/health")
async def model_health(
    predictor: FraudPredictor = Depends(get_predictor),
) -> dict:
    return {
        "status": "healthy",
        "model_loaded": True,
        "feature_count": len(predictor.feature_names),
    }