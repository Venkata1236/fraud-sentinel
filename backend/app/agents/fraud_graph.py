"""
LangGraph 3-tier fraud investigation pipeline.

State flows:
  LOW  (<0.30) → auto_approve_node → log_node
  MED  (0.30–0.70) → flag_review_node → explain_node → report_node
  HIGH (>0.70) → block_investigate_node → escalate_node → report_node
"""

from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END
from loguru import logger
from openai import OpenAI

from app.core.config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

# ─── State ────────────────────────────────────────────────────────────────────

class FraudState(TypedDict):
    transaction_id: str
    amount: float
    timestamp: str
    features: list
    fraud_probability: float
    label: str                  # FRAUD | LEGITIMATE
    confidence: float
    risk_tier: str              # LOW | MEDIUM | HIGH
    top_features: list          # [{feature, raw_value, shap_impact}]
    shap_values: list
    explanation: str            # plain language explanation
    recommended_action: str     # AUTO_APPROVE | FLAG_FOR_REVIEW | BLOCK_AND_ESCALATE
    escalation_reason: str | None
    analyst_notes: str | None
    report: dict | None


# ─── Nodes ────────────────────────────────────────────────────────────────────

def score_node(state: FraudState) -> FraudState:
    """
    Scoring already done before graph entry.
    This node just logs and validates state completeness.
    """
    logger.info(
        f"[score_node] txn={state['transaction_id']} "
        f"prob={state['fraud_probability']:.4f} tier={state['risk_tier']}"
    )
    return state


def confidence_router(state: FraudState) -> Literal["auto_approve", "flag_review", "block_investigate"]:
    """
    Routes based on fraud_probability thresholds.
    This is the branching logic — determines investigation path.
    """
    prob = state["fraud_probability"]
    if prob < 0.30:
        return "auto_approve"
    elif prob < 0.70:
        return "flag_review"
    else:
        return "block_investigate"


def auto_approve_node(state: FraudState) -> FraudState:
    """LOW risk — approve immediately, no human review needed."""
    logger.info(f"[auto_approve] txn={state['transaction_id']} amount=₹{state['amount']:.2f}")
    return {
        **state,
        "recommended_action": "AUTO_APPROVE",
        "explanation": (
            f"Transaction of ₹{state['amount']:.2f} shows low fraud indicators "
            f"(probability: {state['fraud_probability']:.1%}). "
            "Automatically approved — no review required."
        ),
        "escalation_reason": None,
        "analyst_notes": None,
    }


def flag_review_node(state: FraudState) -> FraudState:
    """MEDIUM risk — flag for analyst review."""
    logger.info(f"[flag_review] txn={state['transaction_id']} amount=₹{state['amount']:.2f}")
    return {
        **state,
        "recommended_action": "FLAG_FOR_REVIEW",
        "escalation_reason": None,
    }


def block_investigate_node(state: FraudState) -> FraudState:
    """HIGH risk — block transaction immediately."""
    logger.info(f"[block_investigate] txn={state['transaction_id']} amount=₹{state['amount']:.2f}")

    top = state["top_features"][0] if state["top_features"] else {}
    reason = (
        f"Fraud probability {state['fraud_probability']:.1%} exceeds HIGH threshold. "
        f"Primary trigger: {top.get('feature', 'unknown')} "
        f"(SHAP impact: {top.get('shap_impact', 0):.4f})"
    )

    return {
        **state,
        "recommended_action": "BLOCK_AND_ESCALATE",
        "escalation_reason": reason,
    }


def explain_node(state: FraudState) -> FraudState:
    """
    Generates plain-language explanation using OpenAI.
    Called for MEDIUM and HIGH risk tiers.
    """
    top_features_text = "\n".join([
        f"- {f['feature']}: value={f['raw_value']:.4f}, SHAP impact={f['shap_impact']:.4f}"
        for f in state["top_features"][:5]
    ])

    prompt = f"""You are a fraud analyst at a bank. Explain this transaction risk assessment in 2-3 clear sentences for a human analyst.

Transaction: ₹{state['amount']:.2f}
Fraud Probability: {state['fraud_probability']:.1%}
Risk Tier: {state['risk_tier']}
Label: {state['label']}

Top contributing features (SHAP values — positive = pushes toward fraud):
{top_features_text}

Write a clear, non-technical explanation of WHY this transaction was flagged. Focus on the strongest signals."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.3,
        )
        explanation = response.choices[0].message.content.strip()
    except Exception as e:
        logger.warning(f"OpenAI explain_node failed: {e} — using fallback")
        explanation = (
            f"Transaction flagged with {state['fraud_probability']:.1%} fraud probability. "
            f"Key indicators: {', '.join(f['feature'] for f in state['top_features'][:3])}."
        )

    return {**state, "explanation": explanation}


def escalate_node(state: FraudState) -> FraudState:
    """HIGH risk — generate escalation notes for fraud team."""
    analyst_notes = (
        f"URGENT: Transaction {state['transaction_id']} blocked. "
        f"Amount: ₹{state['amount']:.2f}. "
        f"Fraud probability: {state['fraud_probability']:.1%}. "
        f"Immediate investigation required. "
        f"Top signal: {state['top_features'][0]['feature'] if state['top_features'] else 'N/A'}."
    )
    return {**state, "analyst_notes": analyst_notes}


def log_node(state: FraudState) -> FraudState:
    """LOW risk — just log the auto-approval."""
    logger.info(
        f"[log_node] AUTO_APPROVED txn={state['transaction_id']} "
        f"prob={state['fraud_probability']:.4f}"
    )
    return state


def report_node(state: FraudState) -> FraudState:
    """Final node — assembles structured investigation report."""
    report = {
        "transaction_id": state["transaction_id"],
        "amount": state["amount"],
        "fraud_probability": state["fraud_probability"],
        "label": state["label"],
        "risk_tier": state["risk_tier"],
        "recommended_action": state["recommended_action"],
        "explanation": state.get("explanation", ""),
        "top_features": state["top_features"],
        "escalation_reason": state.get("escalation_reason"),
        "analyst_notes": state.get("analyst_notes"),
    }
    logger.info(f"[report_node] Report assembled for txn={state['transaction_id']}")
    return {**state, "report": report}


# ─── Graph Assembly ───────────────────────────────────────────────────────────

def build_fraud_graph():
    from langgraph.graph import StateGraph, END

    graph = StateGraph(FraudState)

    graph.add_node("score", score_node)
    graph.add_node("auto_approve", auto_approve_node)
    graph.add_node("flag_review", flag_review_node)
    graph.add_node("block_investigate", block_investigate_node)
    graph.add_node("explain", explain_node)
    graph.add_node("escalate", escalate_node)
    graph.add_node("log", log_node)
    graph.add_node("compile_report", report_node)

    graph.set_entry_point("score")

    graph.add_conditional_edges(
        "score",
        confidence_router,
        {
            "auto_approve": "auto_approve",
            "flag_review": "flag_review",
            "block_investigate": "block_investigate",
        }
    )

    graph.add_edge("auto_approve", "log")
    graph.add_edge("log", END)

    graph.add_edge("flag_review", "explain")
    graph.add_edge("explain", "compile_report")
    graph.add_edge("compile_report", END)

    graph.add_edge("block_investigate", "escalate")
    graph.add_edge("escalate", "explain")

    compiled = graph.compile()
    print(f"Graph compiled: {type(compiled)}")  # debug line
    return compiled  # ← THIS LINE IS CRITICAL

# Singleton — compiled once at import
try:
    fraud_graph = build_fraud_graph()
    if fraud_graph is None:
        raise RuntimeError("build_fraud_graph() returned None")
except Exception as e:
    import traceback
    traceback.print_exc()
    raise RuntimeError(f"Failed to build fraud graph: {e}")