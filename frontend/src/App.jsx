import React, { useState, useEffect } from 'react'
import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000'

function App() {
  const [formData, setFormData] = useState({
    amount: 700,
    bank: 'HDFC',
    offerText: '10% cashback up to ₹100 on min ₹500 using HDFC card first transaction',
    isFirstTransaction: true,
  })

  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [backendStatus, setBackendStatus] = useState(null)

  // Check backend status on mount
  useEffect(() => {
    checkBackendStatus()
  }, [])

  const checkBackendStatus = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/health`)
      setBackendStatus(response.data)
    } catch (err) {
      setBackendStatus({
        status: 'offline',
        ollama_available: false,
        error: 'Backend not reachable'
      })
    }
  }

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }))
  }

  const handleCalculate = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const response = await axios.post(`${API_BASE_URL}/calculate`, {
        offer_text: formData.offerText,
        amount: parseFloat(formData.amount),
        bank: formData.bank,
        is_first_transaction: formData.isFirstTransaction,
      })

      setResult(response.data)
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to calculate cashback'
      setError(errorMessage)
      console.error('Error:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleClear = () => {
    setFormData({
      amount: 700,
      bank: 'HDFC',
      offerText: '10% cashback up to ₹100 on min ₹500 using HDFC card first transaction',
      isFirstTransaction: true,
    })
    setResult(null)
    setError(null)
  }

  return (
    <div className="container">
      <div className="header">
        <h1>💰 Cashback Clarity Engine</h1>
        <p>Calculate your cashback instantly with offline AI</p>
      </div>

      {/* Status Bar */}
      {backendStatus && (
        <div className={`status-bar ${backendStatus.status === 'ready' ? 'ok' : backendStatus.status === 'degraded' ? 'warning' : 'error'}`}>
          <span className="status-dot"></span>
          {backendStatus.status === 'ready' ? '✓ Backend Ready' : '⚠ Backend Degraded - Some features may be limited'}
          {backendStatus.ollama_available === false && ' (Ollama offline)'}
        </div>
      )}

      <form onSubmit={handleCalculate}>
        <div className="form-group">
          <label htmlFor="amount">Transaction Amount (₹)</label>
          <input
            type="number"
            id="amount"
            name="amount"
            value={formData.amount}
            onChange={handleInputChange}
            min="1"
            step="0.01"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="bank">Your Bank</label>
          <select
            id="bank"
            name="bank"
            value={formData.bank}
            onChange={handleInputChange}
            required
          >
            <option value="HDFC">HDFC Bank</option>
            <option value="ICICI">ICICI Bank</option>
            <option value="SBI">SBI</option>
            <option value="Axis">Axis Bank</option>
            <option value="Kotak">Kotak Mahindra</option>
            <option value="IDBI">IDBI Bank</option>
            <option value="PNB">Punjab National Bank</option>
            <option value="BOB">Bank of Baroda</option>
            <option value="RBL">RBL Bank</option>
            <option value="IndusInd">IndusInd Bank</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="offerText">Offer Details</label>
          <textarea
            id="offerText"
            name="offerText"
            value={formData.offerText}
            onChange={handleInputChange}
            placeholder="E.g., 10% cashback up to ₹100 on min ₹500 using HDFC card"
            required
          ></textarea>
        </div>

        <div className="form-group checkbox-group">
          <input
            type="checkbox"
            id="isFirstTransaction"
            name="isFirstTransaction"
            checked={formData.isFirstTransaction}
            onChange={handleInputChange}
          />
          <label htmlFor="isFirstTransaction" style={{ margin: 0 }}>
            This is my first transaction
          </label>
        </div>

        <div className="button-group">
          <button type="submit" className="btn-calculate" disabled={loading}>
            {loading ? (
              <span className="loading">
                <span className="spinner"></span> Calculating...
              </span>
            ) : (
              '🚀 Calculate Cashback'
            )}
          </button>
          <button type="button" className="btn-clear" onClick={handleClear}>
            Clear
          </button>
        </div>
      </form>

      {/* Error Display */}
      {error && (
        <div className="result error">
          <div className="result-header">❌ Error</div>
          <div className="explanation">{error}</div>
        </div>
      )}

      {/* Result Display */}
      {result && (
        <div className={`result ${result.eligible ? 'success' : 'error'}`}>
          <div className="result-header">
            {result.eligible ? '✅ Eligible for Cashback' : '❌ Not Eligible'}
          </div>

          {result.eligible && (
            <div className="cashback-amount">₹{result.cashback.toFixed(2)}</div>
          )}

          <div className="explanation">{result.explanation}</div>

          <div className="reasons">
            {result.reasons && result.reasons.length > 0 && (
              <div>
                <div className="reasons-title">✓ Approved Reasons:</div>
                <ul className="reasons-list">
                  {result.reasons.map((reason, idx) => (
                    <li key={idx}>{reason}</li>
                  ))}
                </ul>
              </div>
            )}

            {result.violations && result.violations.length > 0 && (
              <div style={{ marginTop: '10px' }}>
                <div className="reasons-title" style={{ color: '#ff6b6b' }}>✗ Violations:</div>
                <ul className="reasons-list violations-list">
                  {result.violations.map((violation, idx) => (
                    <li key={idx}>{violation}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          <div style={{ marginTop: '15px', padding: '10px', background: '#f0f0f0', borderRadius: '6px', fontSize: '12px', color: '#666' }}>
            <strong>Parsed Offer Details:</strong>
            <ul style={{ marginTop: '8px', marginLeft: '20px' }}>
              <li>Percentage: {result.offer_details.percentage || 'N/A'}%</li>
              <li>Max Cashback: ₹{result.offer_details.max_cashback || 'N/A'}</li>
              <li>Min Transaction: ₹{result.offer_details.min_transaction || 'N/A'}</li>
              <li>Banks: {result.offer_details.banks.join(', ') || 'All'}</li>
              <li>First Transaction Only: {result.offer_details.is_first_transaction ? 'Yes' : 'No'}</li>
            </ul>
          </div>
        </div>
      )}
    </div>
  )
}

export default App
