import { useState, useEffect } from 'react'
import HumanizerForm from './components/HumanizerForm'
import ResultsDisplay from './components/ResultsDisplay'
import Header from './components/Header'
import Footer from './components/Footer'

export default function App() {
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [providerInfo, setProviderInfo] = useState(null)

  // Fetch provider info on mount
  useEffect(() => {
    fetch('/api/provider')
      .then(r => r.json())
      .then(setProviderInfo)
      .catch(() => {})
  }, [])

  const handleHumanize = async (text, tone, language) => {
    setLoading(true)
    setResults(null)
    try {
      const response = await fetch('/api/humanize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, tone, language })
      })
      const data = await response.json()
      if (!response.ok) {
        alert(data.error || 'Error humanizing text')
      } else {
        setResults(data)
      }
    } catch (error) {
      console.error('Error:', error)
      alert('Error humanizing text')
    }
    setLoading(false)
  }

  return (
    <div className="min-h-screen flex flex-col">
      {/* Background decoration */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 rounded-full bg-indigo-500/10 blur-3xl" />
        <div className="absolute top-1/2 -left-40 w-96 h-96 rounded-full bg-cyan-500/10 blur-3xl" />
        <div className="absolute -bottom-40 right-1/3 w-72 h-72 rounded-full bg-purple-500/10 blur-3xl" />
      </div>

      <Header providerInfo={providerInfo} />

      <main className="flex-grow max-w-5xl mx-auto w-full px-4 py-10 relative z-10">
        <HumanizerForm
          onHumanize={handleHumanize}
          loading={loading}
          stageLog={results?.stage_log}
        />
        {results && <ResultsDisplay results={results} />}
      </main>

      <Footer />
    </div>
  )
}
