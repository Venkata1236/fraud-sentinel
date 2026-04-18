from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
import time

from app.models.schemas import PredictRequest, PredictResponse
from app.ml.predict import get_predictor, FraudPredictor

router = APIRouter(prefix="/predict", tags=["Prediction"])


@router.post(
    "",
    response_model=PredictResponse,
    summary="Score a single transaction",
)
async def predict_transaction(
    request: PredictRequest,
    predictor: FraudPredictor = Depends(get_predictor),
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
    logger.info(
        f"Predicted | label={result.label} | "
        f"fraud_prob={result.fraud_probability:.4f} | "
        f"risk={result.risk_tier} | "
        f"latency={elapsed_ms:.2f}ms"
    )

    return result


@router.get("/health", summary="Model health check")
async def model_health(
    predictor: FraudPredictor = Depends(get_predictor),
) -> dict:
    return {
        "status": "healthy",
        "model_loaded": True,
        "feature_count": len(predictor.feature_names),
        "feature_names_sample": predictor.feature_names[:5],
    }