import { useState } from 'react'

const defaultValues = {
  amount: 250.00,
  time: 43200,
  v1: -1.36,
  v2: -0.07,
  v3: 2.54,
  v4: 1.38,
}

export default function TransactionForm({ onSubmit, isLoading }) {
  const [values, setValues] = useState(defaultValues)

  const handleChange = (key) => (e) => {
    setValues(prev => ({ ...prev, [key]: parseFloat(e.target.value) || 0 }))
  }

  const buildFeatures = () => {
    // Build 30-feature array: [Time, V1-V28, Amount]
    // V5-V28 default to 0 for demo — real system would take full input
    const features = [
      values.time,
      values.v1, values.v2, values.v3, values.v4,
      // V5–V28: zeros for demo
      ...Array(24).fill(0),
      values.amount,
    ]
    return features
  }

  const handleSubmit = () => {
    onSubmit({
      transaction_id: `TXN-${Date.now()}`,
      amount: values.amount,
      timestamp: new Date().toISOString(),
      features: buildFeatures(),
    })
  }

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5">
      <h2 className="text-base font-semibold text-gray-800 mb-4">
        Transaction Details
      </h2>

      <div className="grid grid-cols-2 gap-4">
        {/* Amount */}
        <div className="col-span-2">
          <label className="block text-xs font-medium text-gray-600 mb-1">
            Amount (₹)
          </label>
          <input
            type="number"
            value={values.amount}
            onChange={handleChange('amount')}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            min={0}
            step={0.01}
          />
        </div>

        {/* Time */}
        <div className="col-span-2">
          <label className="block text-xs font-medium text-gray-600 mb-1">
            Time (seconds since first transaction: {values.time.toLocaleString()})
          </label>
          <input
            type="range"
            min={0}
            max={172792}
            value={values.time}
            onChange={handleChange('time')}
            className="w-full accent-blue-500"
          />
          <div className="flex justify-between text-xs text-gray-400 mt-1">
            <span>0</span><span>~48hrs</span>
          </div>
        </div>

        {/* V1–V4 */}
        {[1,2,3,4].map(i => (
          <div key={i}>
            <label className="block text-xs font-medium text-gray-600 mb-1">
              V{i} <span className="text-gray-400">(PCA feature)</span>
            </label>
            <input
              type="number"
              value={values[`v${i}`]}
              onChange={handleChange(`v${i}`)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              step={0.01}
            />
          </div>
        ))}
      </div>

      <button
        onClick={handleSubmit}
        disabled={isLoading}
        className={`mt-5 w-full py-2.5 rounded-lg text-sm font-semibold text-white transition
          ${isLoading
            ? 'bg-gray-400 cursor-not-allowed'
            : 'bg-blue-600 hover:bg-blue-700 active:bg-blue-800'
          }`}
      >
        {isLoading ? (
          <span className="flex items-center justify-center gap-2">
            <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
            </svg>
            Analyzing...
          </span>
        ) : '🔍 Analyze Transaction'}
      </button>
    </div>
  )
}