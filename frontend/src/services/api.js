import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: { 'Content-Type': 'application/json' },
})

export const predictTransaction = (features) =>
  api.post('/predict', { features })

export const analyzeTransaction = (payload) =>
  api.post('/analyze', payload)

export default api