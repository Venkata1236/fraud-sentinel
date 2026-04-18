import { useState } from 'react'
import { Toaster, toast } from 'react-hot-toast'
import TransactionForm from '../components/TransactionForm'
import RiskMeter from '../components/RiskMeter'
import SHAPChart from '../components/SHAPChart'
import ExplanationCard from '../components/ExplanationCard'
import { analyzeTransaction } from '../services/api'

export default function Dashboard() {
  const [isLoading, setIsLoading] = useState(false)
  const [result, setResult] = useState(null)

  const handleAnalyze = async (payload) => {
    setIsLoading(true)
    setResult(null)
    try {
      const res = await analyzeTransaction(payload)
      setResult(res.data)
      const tier = res.data.report?.risk_tier
      if (tier === 'HIGH') toast.error('🚨 HIGH RISK — Transaction Blocked')
      else if (tier === 'MEDIUM') toast('⚠️ MEDIUM RISK — Flagged for Review', { icon: '⚠️' })
      else toast.success('✅ LOW RISK — Auto Approved')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Analysis failed')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Toaster position="top-right" />

      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="max-w-5xl mx-auto flex items-center gap-3">
          <span className="text-2xl">🛡️</span>
          <div>
            <h1 className="text-lg font-bold text-gray-900">FraudSentinel</h1>
            <p className="text-xs text-gray-500">Real-time fraud detection • XGBoost + SHAP + LangGraph</p>
          </div>
        </div>
      </div>

      {/* Main */}
      <div className="max-w-5xl mx-auto px-6 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

          {/* Left — Form + RiskMeter */}
          <div className="space-y-6">
            <TransactionForm onSubmit={handleAnalyze} isLoading={isLoading} />

            {result?.report && (
              <div className="bg-white rounded-xl border border-gray-200 p-5 flex flex-col items-center">
                <h3 className="text-sm font-semibold text-gray-700 mb-3">Risk Score</h3>
                <RiskMeter
                  probability={result.report.fraud_probability}
                  tier={result.report.risk_tier}
                />
                <p className="text-xs text-gray-500 mt-2">
                  Confidence: {(result.report.fraud_probability * 100).toFixed(1)}% fraud probability
                </p>
              </div>
            )}
          </div>

          {/* Right — SHAP + Explanation */}
          <div className="space-y-6">
            {result?.report && (
              <>
                <div className="bg-white rounded-xl border border-gray-200 p-5">
                  <SHAPChart topFeatures={result.report.top_features} />
                </div>
                <ExplanationCard report={result.report} />
              </>
            )}

            {!result && !isLoading && (
              <div className="bg-white rounded-xl border border-dashed border-gray-300 p-10 flex flex-col items-center justify-center text-center">
                <span className="text-4xl mb-3">🔍</span>
                <p className="text-sm text-gray-500">Submit a transaction to see the risk analysis</p>
                <p className="text-xs text-gray-400 mt-1">Results will appear here</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}