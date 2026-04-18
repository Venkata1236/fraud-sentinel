"""
POST /analyze — full LangGraph investigation pipeline.
Calls /predict internally then routes through LangGraph.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
from datetime import datetime
import uuid
import time

from app.models.schemas import AnalyzeRequest, AnalyzeResponse, InvestigationReport, TopFeature
from app.ml.predict import get_predictor, FraudPredictor
from app.agents.fraud_graph import fraud_graph

router = APIRouter(prefix="/analyze", tags=["Analysis"])


@router.post(
    "",
    response_model=AnalyzeResponse,
    summary="Full fraud investigation pipeline",
    description=(
        "Runs XGBoost scoring + SHAP explanation + LangGraph routing. "
        "Returns structured investigation report with recommended action."
    ),
)
async def analyze_transaction(
    request: AnalyzeRequest,
    predictor: FraudPredictor = Depends(get_predictor),
) -> AnalyzeResponse:
    start = time.perf_counter()

    try:
        # Step 1 — ML scoring + SHAP
        prediction = predictor.predict(request.features)

        # Step 2 — Build initial LangGraph state
        initial_state = {
            "transaction_id": request.transaction_id,
            "amount": request.amount,
            "timestamp": request.timestamp.isoformat(),
            "features": request.features,
            "fraud_probability": prediction.fraud_probability,
            "label": prediction.label,
            "confidence": prediction.confidence,
            "risk_tier": prediction.risk_tier,
            "top_features": [f.model_dump() for f in prediction.top_features],
            "shap_values": prediction.shap_values,
            "explanation": "",
            "recommended_action": "",
            "escalation_reason": None,
            "analyst_notes": None,
            "report": None,
        }

        # Step 3 — Run LangGraph pipeline
        final_state = fraud_graph.invoke(initial_state)

        elapsed_ms = (time.perf_counter() - start) * 1000
        logger.info(
            f"Analyzed | txn={request.transaction_id} | "
            f"action={final_state['recommended_action']} | "
            f"latency={elapsed_ms:.2f}ms"
        )

        # Step 4 — Build response
        # LOW tier goes through log_node not report_node, so report may be None
        if final_state.get("report"):
            report_data = final_state["report"]
        else:
            # AUTO_APPROVE path — build report from state
            report_data = {
                "transaction_id": request.transaction_id,
                "amount": request.amount,
                "fraud_probability": prediction.fraud_probability,
                "label": prediction.label,
                "risk_tier": prediction.risk_tier,
                "recommended_action": final_state.get("recommended_action", "AUTO_APPROVE"),
                "explanation": final_state.get("explanation", ""),
                "top_features": [f.model_dump() for f in prediction.top_features],
                "escalation_reason": None,
                "analyst_notes": None,
            }

        report = InvestigationReport(
            transaction_id=report_data["transaction_id"],
            risk_tier=report_data["risk_tier"],
            fraud_probability=report_data["fraud_probability"],
            recommended_action=report_data["recommended_action"],
            explanation=report_data["explanation"],
            top_features=[TopFeature(**f) for f in report_data["top_features"]],
            escalation_reason=report_data.get("escalation_reason"),
            analyst_notes=report_data.get("analyst_notes"),
        )

        return AnalyzeResponse(status="completed", report=report)

    except Exception as e:
        logger.error(f"Analysis failed for txn={request.transaction_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis error: {str(e)}",
        )