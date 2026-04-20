# 🛡️ FraudSentinel — Real-Time Banking Fraud Detection

> Production-grade fraud detection system — XGBoost + SHAP + LangGraph + React

[![Live Demo](https://img.shields.io/badge/Live-Demo-blue)](https://fraud-sentinel.vercel.app)
[![API Docs](https://img.shields.io/badge/API-Docs-green)](https://fraud-sentinel-api.onrender.com/docs)
[![GitHub](https://img.shields.io/badge/GitHub-Repo-black)](https://github.com/Venkata1236/fraud-sentinel)

---

## 🏦 Real-World Problem

HDFC Bank processes 50,000+ transactions daily. 0.17% are fraudulent — each
missed fraud costs ₹2–15 lakhs. FraudSentinel scores every transaction
in real-time, explains WHY it was flagged, and routes it through a 3-tier
investigation pipeline.

---

## 🏗️ Architecture
React Dashboard → FastAPI /predict → XGBoost Model
↓
SHAP TreeExplainer
↓
FastAPI /analyze → LangGraph Pipeline
↓
┌─────────────────────────────┐
LOW (<0.3)    MEDIUM (0.3-0.7)   HIGH (>0.7)
↓              ↓                ↓
AutoApprove     FlagReview      BlockInvestigate
↓              ↓                ↓
LogNode      ExplainNode      EscalateNode
↓                ↓
CompileReport ←────────┘
↓
PostgreSQL Storage

---

## 🤖 Tech Stack

| Layer | Technology |
|---|---|
| ML Model | XGBoost + SMOTE |
| Explainability | SHAP TreeExplainer |
| Agent Pipeline | LangGraph StateGraph |
| Backend | FastAPI (async) |
| Database | PostgreSQL + SQLAlchemy async |
| Frontend | React + Vite + TailwindCSS + Recharts |
| Containerization | Docker + docker-compose |
| Deployment | Vercel (React) + Render (FastAPI) |

---

## 📊 Model Performance

| Metric | Score |
|---|---|
| F1 Score (Fraud) | > 0.80 |
| ROC-AUC | > 0.97 |
| Inference Latency | < 5ms |
| Training Strategy | StratifiedKFold 5-fold |

---

## 🚀 Quick Start

```bash
# Clone
git clone https://github.com/Venkata1236/fraud-sentinel
cd fraud-sentinel

# Train model first
cd backend/notebooks
jupyter notebook eda_training.ipynb

# Run with Docker
cd ../..
docker-compose up --build

# Or run manually
cd backend
python -m uvicorn app.main:app --reload --port 8000

cd ../frontend
npm install && npm run dev
```

---

## 🔗 Live URLs

- **Frontend:** https://fraud-sentinel.vercel.app
- **API Docs:** https://fraud-sentinel-api.onrender.com/docs
- **GitHub:** https://github.com/Venkata1236/fraud-sentinel