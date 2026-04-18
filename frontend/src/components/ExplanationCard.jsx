const tierStyles = {
  LOW:    { bg: 'bg-green-50',  border: 'border-green-200', badge: 'bg-green-100 text-green-800',  icon: '✅' },
  MEDIUM: { bg: 'bg-yellow-50', border: 'border-yellow-200', badge: 'bg-yellow-100 text-yellow-800', icon: '⚠️' },
  HIGH:   { bg: 'bg-red-50',    border: 'border-red-200',    badge: 'bg-red-100 text-red-800',       icon: '🚨' },
}

const actionLabels = {
  AUTO_APPROVE:       { label: 'Auto Approved',      color: 'text-green-700' },
  FLAG_FOR_REVIEW:    { label: 'Flagged for Review', color: 'text-yellow-700' },
  BLOCK_AND_ESCALATE: { label: 'Blocked & Escalated', color: 'text-red-700' },
}

export default function ExplanationCard({ report }) {
  if (!report) return null

  const tier = report.risk_tier || 'LOW'
  const styles = tierStyles[tier]
  const action = actionLabels[report.recommended_action] || actionLabels.AUTO_APPROVE

  return (
    <div className={`rounded-xl border ${styles.border} ${styles.bg} p-5`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <span className="text-xl">{styles.icon}</span>
          <span className={`text-xs font-bold px-2 py-1 rounded-full ${styles.badge}`}>
            {tier} RISK
          </span>
        </div>
        <span className={`text-sm font-semibold ${action.color}`}>
          {action.label}
        </span>
      </div>

      {/* Explanation */}
      {report.explanation && (
        <div className="mb-4">
          <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">
            AI Explanation
          </p>
          <p className="text-sm text-gray-700 leading-relaxed">
            {report.explanation}
          </p>
        </div>
      )}

      {/* Escalation reason */}
      {report.escalation_reason && (
        <div className="mb-4 p-3 bg-red-100 rounded-lg border border-red-200">
          <p className="text-xs font-semibold text-red-700 uppercase mb-1">Escalation Reason</p>
          <p className="text-sm text-red-800">{report.escalation_reason}</p>
        </div>
      )}

      {/* Analyst notes */}
      {report.analyst_notes && (
        <div className="p-3 bg-orange-50 rounded-lg border border-orange-200">
          <p className="text-xs font-semibold text-orange-700 uppercase mb-1">Analyst Notes</p>
          <p className="text-sm text-orange-800">{report.analyst_notes}</p>
        </div>
      )}

      {/* Transaction ID */}
      <p className="text-xs text-gray-400 mt-4 font-mono">
        TXN: {report.transaction_id}
      </p>
    </div>
  )
}