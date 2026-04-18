import { useState } from 'react'

export default function ResultsDisplay({ results }) {
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    await navigator.clipboard.writeText(results.humanized)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const handleDownload = () => {
    const element = document.createElement('a')
    const file = new Blob([results.humanized], { type: 'text/plain' })
    element.href = URL.createObjectURL(file)
    element.download = 'humanized_text.txt'
    document.body.appendChild(element)
    element.click()
    document.body.removeChild(element)
  }

  const scoreDrop = results.ai_score_before - results.ai_score_after

  return (
    <div className="mt-10 glass rounded-2xl p-8 animate-in" id="results-section">
      {/* Header */}
      <div className="flex items-center gap-3 mb-8">
        <div className="w-10 h-10 rounded-xl bg-emerald-500/20 flex items-center justify-center">
          <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <h2 className="text-2xl font-bold text-white">Results</h2>
        {scoreDrop > 0 && (
          <span className="ml-auto px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-sm font-medium">
            ↓ {scoreDrop}% AI score reduction
          </span>
        )}
      </div>

      {/* AI Score Comparison */}
      <div className="mb-8 p-5 rounded-xl bg-slate-800/50 border border-slate-700/50">
        <h3 className="font-semibold text-sm text-slate-300 uppercase tracking-wider mb-5">AI Detection Score</h3>

        {/* Before */}
        <div className="mb-4">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm text-slate-400">Original Text</span>
            <span className="text-sm font-bold text-red-400">{results.ai_score_before}%</span>
          </div>
          <div className="w-full h-2.5 rounded-full bg-slate-700/50 overflow-hidden">
            <div
              className="h-full rounded-full transition-all duration-1000 ease-out"
              style={{
                width: `${results.ai_score_before}%`,
                background: 'linear-gradient(90deg, #ef4444, #f87171)'
              }}
            />
          </div>
        </div>

        {/* After */}
        <div>
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm text-slate-400">Humanized Text</span>
            <span className="text-sm font-bold text-emerald-400">{results.ai_score_after}%</span>
          </div>
          <div className="w-full h-2.5 rounded-full bg-slate-700/50 overflow-hidden">
            <div
              className="h-full rounded-full transition-all duration-1000 ease-out"
              style={{
                width: `${results.ai_score_after}%`,
                background: 'linear-gradient(90deg, #10b981, #34d399)'
              }}
            />
          </div>
        </div>
      </div>

      {/* Detected Patterns */}
      {results.patterns_removed && results.patterns_removed.length > 0 && (
        <div className="mb-8 p-5 rounded-xl bg-amber-500/5 border border-amber-500/20">
          <h3 className="font-semibold text-sm text-amber-400 uppercase tracking-wider mb-3">
            Patterns Removed
          </h3>
          <div className="flex flex-wrap gap-2">
            {results.patterns_removed.map((pattern, i) => (
              <span
                key={i}
                className="px-3 py-1 rounded-lg bg-amber-500/10 text-amber-300 text-sm border border-amber-500/20"
              >
                {pattern}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Humanized Text */}
      <div className="mb-8">
        <h3 className="font-semibold text-sm text-slate-300 uppercase tracking-wider mb-3">
          Humanized Text
        </h3>
        <div className="p-5 rounded-xl bg-emerald-500/5 border border-emerald-500/20">
          <p className="text-slate-200 whitespace-pre-wrap leading-relaxed" id="humanized-output">
            {results.humanized}
          </p>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-3">
        <button
          onClick={handleCopy}
          id="copy-button"
          className="flex-1 py-3 rounded-xl font-semibold text-white flex items-center justify-center gap-2 transition-smooth hover:scale-[1.02] active:scale-[0.98]"
          style={{ background: 'linear-gradient(135deg, #6366f1, #818cf8)' }}
        >
          {copied ? (
            <>
              <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
              </svg>
              Copied!
            </>
          ) : (
            <>
              <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
              Copy to Clipboard
            </>
          )}
        </button>
        <button
          onClick={handleDownload}
          id="download-button"
          className="flex-1 py-3 rounded-xl font-semibold text-white flex items-center justify-center gap-2 transition-smooth hover:scale-[1.02] active:scale-[0.98]"
          style={{ background: 'linear-gradient(135deg, #10b981, #34d399)' }}
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          Download TXT
        </button>
      </div>
    </div>
  )
}
