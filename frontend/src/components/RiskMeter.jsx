/**
 * Semicircular SVG gauge showing fraud probability.
 * 0–30%: green (LOW), 30–70%: yellow (MEDIUM), 70–100%: red (HIGH)
 */

const RADIUS = 80
const STROKE = 16
const CENTER = 100
const CIRCUMFERENCE = Math.PI * RADIUS  // semicircle

const tierColor = {
  LOW: '#22c55e',
  MEDIUM: '#f59e0b',
  HIGH: '#ef4444',
}

export default function RiskMeter({ probability = 0, tier = 'LOW' }) {
  // Convert probability (0–1) to stroke offset
  const progress = Math.min(Math.max(probability, 0), 1)
  const offset = CIRCUMFERENCE * (1 - progress)
  const color = tierColor[tier] || '#22c55e'
  const percentage = Math.round(progress * 100)

  return (
    <div className="flex flex-col items-center">
      <svg width="200" height="120" viewBox="0 0 200 120">
        {/* Background arc */}
        <path
          d={`M ${CENTER - RADIUS} ${CENTER} A ${RADIUS} ${RADIUS} 0 0 1 ${CENTER + RADIUS} ${CENTER}`}
          fill="none"
          stroke="#e5e7eb"
          strokeWidth={STROKE}
          strokeLinecap="round"
        />
        {/* Foreground arc — animated */}
        <path
          d={`M ${CENTER - RADIUS} ${CENTER} A ${RADIUS} ${RADIUS} 0 0 1 ${CENTER + RADIUS} ${CENTER}`}
          fill="none"
          stroke={color}
          strokeWidth={STROKE}
          strokeLinecap="round"
          strokeDasharray={CIRCUMFERENCE}
          strokeDashoffset={offset}
          style={{ transition: 'stroke-dashoffset 0.8s ease, stroke 0.3s ease' }}
        />
        {/* Percentage text */}
        <text
          x={CENTER}
          y={CENTER - 10}
          textAnchor="middle"
          fontSize="28"
          fontWeight="bold"
          fill={color}
        >
          {percentage}%
        </text>
        {/* Tier label */}
        <text
          x={CENTER}
          y={CENTER + 14}
          textAnchor="middle"
          fontSize="13"
          fill="#6b7280"
        >
          {tier} RISK
        </text>
        {/* Zone labels */}
        <text x="18" y="115" fontSize="10" fill="#22c55e">LOW</text>
        <text x="88" y="32" fontSize="10" fill="#f59e0b">MED</text>
        <text x="163" y="115" fontSize="10" fill="#ef4444">HIGH</text>
      </svg>
    </div>
  )
}