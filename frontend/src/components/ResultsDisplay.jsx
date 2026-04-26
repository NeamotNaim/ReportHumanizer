import { useState } from 'react'

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
    element.download = 'revised_draft.txt'
    document.body.appendChild(element)
    element.click()
    document.body.removeChild(element)
  }

  const scoreDrop = results.ai_score_before - results.ai_score_after
  const beforeIssues = results.analysis_before?.issues || []
  const afterIssues = results.analysis_after?.issues || []
  const iterations = results.iterations || 0
  const stageLog = results.stage_log || []
  const provider = results.provider || 'unknown'
  const wordCountOriginal = results.word_count_original || 0
  const wordCountHumanized = results.word_count_humanized || 0

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
          <h2 className="text-2xl font-bold text-white">Revision Results</h2>
        </div>
        <div className="flex items-center gap-3">
          {iterations > 0 && (
            <span className="px-3 py-1.5 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-300 text-xs font-medium">
              {iterations} refinement pass{iterations > 1 ? 'es' : ''}
            </span>
          )}
          {scoreDrop > 0 && (
            <span className="px-4 py-2 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-sm font-bold shadow-[0_0_15px_rgba(16,185,129,0.2)]">
              {scoreDrop}% lower heuristic score
            </span>
          )}
        </div>
      </div>

      {/* Pipeline Summary */}
      {stageLog.length > 0 && (
        <div className="mb-6 p-4 rounded-xl bg-slate-800/50 border border-slate-700/30">
          <button
            onClick={(e) => {
              const el = e.currentTarget.nextElementSibling
              el.style.display = el.style.display === 'none' ? 'block' : 'none'
            }}
            className="flex items-center gap-2 text-sm font-medium text-slate-400 hover:text-slate-200 transition-colors w-full"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
            </svg>
            Pipeline Log ({stageLog.length} steps) — Powered by {provider}
          </button>
          <div style={{ display: 'none' }} className="mt-3 space-y-1">
            {stageLog.map((log, i) => (
              <p key={i} className={`text-xs font-mono ${log.startsWith('  ') ? 'text-slate-500 pl-3' : 'text-slate-300'}`}>
                {log}
              </p>
            ))}
          </div>
        </div>
      )}

      {/* Stats Row */}
      <div className="mb-8 grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl bg-slate-800/60 border border-slate-700/30 text-center">
          <p className="text-2xl font-bold text-red-400">{results.ai_score_before}</p>
          <p className="text-xs text-slate-500 mt-1">Score Before</p>
        </div>
        <div className="p-4 rounded-xl bg-slate-800/60 border border-slate-700/30 text-center">
          <p className="text-2xl font-bold text-emerald-400">{results.ai_score_after}</p>
          <p className="text-xs text-slate-500 mt-1">Score After</p>
        </div>
        <div className="p-4 rounded-xl bg-slate-800/60 border border-slate-700/30 text-center">
          <p className="text-2xl font-bold text-slate-200">{wordCountOriginal}</p>
          <p className="text-xs text-slate-500 mt-1">Words Original</p>
        </div>
        <div className="p-4 rounded-xl bg-slate-800/60 border border-slate-700/30 text-center">
          <p className={`text-2xl font-bold ${Math.abs(wordCountHumanized - wordCountOriginal) / Math.max(wordCountOriginal, 1) > 0.15 ? 'text-amber-400' : 'text-slate-200'}`}>
            {wordCountHumanized}
          </p>
          <p className="text-xs text-slate-500 mt-1">Words Revised</p>
        </div>
      </div>

      {/* Heuristic comparison bars */}
      <div className="mb-8 p-6 rounded-xl bg-slate-800/80 border border-slate-700/50 shadow-lg">
        <h3 className="font-semibold text-sm text-slate-400 uppercase tracking-wider mb-5 flex items-center gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg>
          Local Writing Heuristics
        </h3>

        <div className="grid md:grid-cols-2 gap-6">
          {/* Before */}
          <div className="bg-slate-900/50 p-4 rounded-lg">
            <div className="flex justify-between items-center mb-3">
              <span className="text-sm text-slate-400">Before Revision</span>
              <span className="text-xl font-bold text-red-400">{results.ai_score_before}</span>
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
              <span className="text-sm text-slate-400">After Revision</span>
              <span className="text-xl font-bold text-emerald-400">{results.ai_score_after}</span>
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

        <p className="mt-4 text-sm text-slate-400 leading-relaxed">
          {results.assessment_note}
        </p>
      </div>

      <div className="mb-8 grid md:grid-cols-2 gap-6">
        <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-700/50">
          <h3 className="text-sm uppercase tracking-wider text-slate-400 mb-3">Issues Found Before</h3>
          <div className="space-y-2">
            {beforeIssues.length ? beforeIssues.map((issue) => (
              <p key={issue} className="text-slate-200 leading-relaxed">{issue}</p>
            )) : (
              <p className="text-slate-300">No major structural issues were flagged by the local analyzer.</p>
            )}
          </div>
        </div>

        <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-700/50">
          <h3 className="text-sm uppercase tracking-wider text-slate-400 mb-3">Issues Still Present After</h3>
          <div className="space-y-2">
            {afterIssues.length ? afterIssues.map((issue) => (
              <p key={issue} className="text-slate-200 leading-relaxed">{issue}</p>
            )) : (
              <p className="text-emerald-300">The revised draft no longer triggered the current structural warnings.</p>
            )}
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
              Copy Revision
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
          Export TXT
        </button>
      </div>
    </div>
  )
}
