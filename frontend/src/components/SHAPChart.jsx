/**
 * Horizontal bar chart showing top 5 SHAP feature impacts.
 * Positive (red) = pushes toward FRAUD
 * Negative (green) = pushes toward LEGITIMATE
 */

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Cell, ResponsiveContainer } from 'recharts'

const CustomTooltip = ({ active, payload }) => {
  if (active && payload && payload.length) {
    const d = payload[0].payload
    return (
      <div className="bg-white border border-gray-200 rounded-lg p-3 shadow-lg text-sm">
        <p className="font-semibold text-gray-800">{d.feature}</p>
        <p className="text-gray-600">Value: <span className="font-mono">{d.raw_value?.toFixed(4)}</span></p>
        <p style={{ color: d.shap_impact >= 0 ? '#ef4444' : '#22c55e' }}>
          SHAP: {d.shap_impact >= 0 ? '+' : ''}{d.shap_impact?.toFixed(4)}
        </p>
        <p className="text-xs text-gray-500 mt-1">
          {d.shap_impact >= 0 ? '↑ Pushes toward FRAUD' : '↓ Pushes toward LEGITIMATE'}
        </p>
      </div>
    )
  }
  return null
}

export default function SHAPChart({ topFeatures = [] }) {
  if (!topFeatures.length) return null

  const data = topFeatures.map(f => ({
    feature: f.feature,
    raw_value: f.raw_value,
    shap_impact: f.shap_impact,
    abs_impact: Math.abs(f.shap_impact),
  }))

  return (
    <div className="w-full">
      <h3 className="text-sm font-semibold text-gray-700 mb-3">
        Top Feature Contributions (SHAP)
      </h3>
      <ResponsiveContainer width="100%" height={200}>
        <BarChart data={data} layout="vertical" margin={{ left: 20, right: 30 }}>
          <CartesianGrid strokeDasharray="3 3" horizontal={false} />
          <XAxis
            type="number"
            tickFormatter={v => v.toFixed(2)}
            fontSize={11}
            label={{ value: 'SHAP Impact', position: 'insideBottom', offset: -2, fontSize: 11 }}
          />
          <YAxis
            type="category"
            dataKey="feature"
            fontSize={11}
            width={40}
          />
          <Tooltip content={<CustomTooltip />} />
          <Bar dataKey="shap_impact" radius={[0, 4, 4, 0]}>
            {data.map((entry, idx) => (
              <Cell
                key={idx}
                fill={entry.shap_impact >= 0 ? '#ef4444' : '#22c55e'}
                fillOpacity={0.85}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <p className="text-xs text-gray-400 mt-2 text-center">
        🔴 Red = pushes toward fraud &nbsp;|&nbsp; 🟢 Green = pushes toward legitimate
      </p>
    </div>
  )
}