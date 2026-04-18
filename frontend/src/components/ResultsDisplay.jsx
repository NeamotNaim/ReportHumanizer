import { useState, useEffect } from 'react'

export default function ResultsDisplay({ results }) {
  const [copied, setCopied] = useState(false)
  const [showDiff, setShowDiff] = useState(true)

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
    <div className="mt-10 glass rounded-2xl p-8 transition-smooth" id="results-section" style={{ animation: 'float 2s ease-out' }}>
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-emerald-500/20 flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-white">Results</h2>
        </div>
        {scoreDrop > 0 && (
          <span className="px-4 py-2 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-sm font-bold shadow-[0_0_15px_rgba(16,185,129,0.2)]">
            📉 {scoreDrop}% AI score reduction
          </span>
        )}
      </div>

      {/* AI Score Comparison */}
      <div className="mb-8 p-6 rounded-xl bg-slate-800/80 border border-slate-700/50 shadow-lg">
        <h3 className="font-semibold text-sm text-slate-400 uppercase tracking-wider mb-5 flex items-center gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg>
          Detection Analysis
        </h3>

        <div className="grid md:grid-cols-2 gap-6">
          {/* Before */}
          <div className="bg-slate-900/50 p-4 rounded-lg">
            <div className="flex justify-between items-center mb-3">
              <span className="text-sm text-slate-400">Original Score</span>
              <span className="text-xl font-bold text-red-400">{results.ai_score_before}% AI</span>
            </div>
            <div className="w-full h-3 rounded-full bg-slate-800 overflow-hidden shadow-inner">
              <div
                className="h-full rounded-full transition-all duration-1000 ease-out"
                style={{
                  width: `${Math.max(results.ai_score_before, 5)}%`,
                  background: 'linear-gradient(90deg, #b91c1c, #ef4444)'
                }}
              />
            </div>
          </div>

          {/* After */}
          <div className="bg-slate-900/50 p-4 rounded-lg">
            <div className="flex justify-between items-center mb-3">
              <span className="text-sm text-slate-400">Humanized Score</span>
              <span className="text-xl font-bold text-emerald-400">{results.ai_score_after}% AI</span>
            </div>
            <div className="w-full h-3 rounded-full bg-slate-800 overflow-hidden shadow-inner">
              <div
                className="h-full rounded-full transition-all duration-1000 ease-out"
                style={{
                  width: `${Math.max(results.ai_score_after, 5)}%`,
                  background: 'linear-gradient(90deg, #047857, #10b981)'
                }}
              />
            </div>
          </div>
        </div>
      </div>

      <div className="mb-4 flex justify-end gap-2">
         <button onClick={() => setShowDiff(false)} className={`px-4 py-1.5 rounded-lg text-sm font-medium transition-all ${!showDiff ? 'bg-indigo-500 text-white shadow-lg' : 'bg-slate-800 text-slate-400 hover:bg-slate-700'}`}>
            Final Text
         </button>
         <button onClick={() => setShowDiff(true)} className={`px-4 py-1.5 rounded-lg text-sm font-medium transition-all ${showDiff ? 'bg-indigo-500 text-white shadow-lg' : 'bg-slate-800 text-slate-400 hover:bg-slate-700'}`}>
            Show Changes
         </button>
      </div>

      {/* Humanized Text / Diff Viewer */}
      <div className="mb-8 relative group">
        <div className="p-6 rounded-xl bg-slate-900/80 border border-slate-700/50 shadow-inner min-h-[150px]">
          {showDiff && results.diff ? (
             <div className="text-slate-300 leading-relaxed font-serif text-lg">
                {results.diff.map((part, i) => {
                   if (part.type === 'added') {
                       return <span key={i} className="bg-emerald-500/20 text-emerald-300 px-1 rounded-sm mx-0.5 inline-block">{part.value}</span>
                   } else if (part.type === 'removed') {
                       return <span key={i} className="bg-red-500/20 text-red-400/70 line-through px-1 rounded-sm mx-0.5 inline-block decoration-red-500/50">{part.value}</span>
                   } else {
                       return <span key={i}>{part.value} </span>
                   }
                })}
             </div>
          ) : (
             <p className="text-slate-200 whitespace-pre-wrap leading-relaxed font-serif text-lg" id="humanized-output">
               {results.humanized}
             </p>
          )}
        </div>
        
        {/* Helper text for diff mode */}
        {showDiff && results.diff && (
           <div className="absolute top-4 right-4 flex gap-3 text-xs font-mono">
              <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-red-400"></span> Removed</span>
              <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-emerald-400"></span> Added</span>
           </div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="flex gap-4">
        <button
          onClick={handleCopy}
          id="copy-button"
          className="flex-1 py-4 rounded-xl font-semibold text-white flex items-center justify-center gap-2 transition-all hover:scale-[1.02] active:scale-[0.98] shadow-lg hover:shadow-indigo-500/25"
          style={{ background: 'linear-gradient(135deg, #6366f1, #818cf8)' }}
        >
          {copied ? (
            <>
              <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
              </svg>
              Copied to Clipboard!
            </>
          ) : (
            <>
              <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
              Copy Text
            </>
          )}
        </button>
        <button
          onClick={handleDownload}
          id="download-button"
          className="flex-1 py-4 rounded-xl font-semibold text-white flex items-center justify-center gap-2 transition-all hover:scale-[1.02] active:scale-[0.98] shadow-lg hover:shadow-emerald-500/25"
          style={{ background: 'linear-gradient(135deg, #10b981, #34d399)' }}
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          Export as TXT
        </button>
      </div>
    </div>
  )
}
