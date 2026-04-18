import { useState } from 'react'

export default function HumanizerForm({ onHumanize, loading }) {
  const [text, setText] = useState('')
  const [tone, setTone] = useState('casual')
  const [language, setLanguage] = useState('en')

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!text.trim()) {
      alert('Please enter some text')
      return
    }
    onHumanize(text, tone, language)
  }

  const handleFileUpload = async (e) => {
    const uploadedFile = e.target.files[0]
    if (!uploadedFile) return

    const formData = new FormData()
    formData.append('file', uploadedFile)

    try {
      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData
      })
      const data = await response.json()
      if (data.text) {
        setText(data.text)
      }
    } catch (error) {
      alert('Error uploading file: ' + error.message)
    }
  }

  const charPercent = Math.min((text.length / 10000) * 100, 100)

  return (
    <form onSubmit={handleSubmit} className="glass rounded-2xl p-8 glow" id="humanizer-form">
      <div className="flex items-center gap-3 mb-8">
        <div className="w-10 h-10 rounded-xl bg-indigo-500/20 flex items-center justify-center">
          <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
          </svg>
        </div>
        <h2 className="text-2xl font-bold text-white">Humanize Your Text</h2>
      </div>

      {/* Tone & Language Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">Tone</label>
          <select
            value={tone}
            onChange={(e) => setTone(e.target.value)}
            id="tone-select"
            className="w-full px-4 py-3 rounded-xl bg-slate-800/80 border border-slate-600/50 text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500/50 transition-smooth appearance-none cursor-pointer"
          >
            <option value="casual">🗣️ Casual</option>
            <option value="academic">🎓 Academic</option>
            <option value="formal">💼 Formal</option>
            <option value="creative">🎨 Creative</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">Language</label>
          <select
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            id="language-select"
            className="w-full px-4 py-3 rounded-xl bg-slate-800/80 border border-slate-600/50 text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500/50 transition-smooth appearance-none cursor-pointer"
          >
            <option value="en">🇬🇧 English</option>
            <option value="es">🇪🇸 Spanish</option>
            <option value="fr">🇫🇷 French</option>
            <option value="de">🇩🇪 German</option>
            <option value="pt">🇵🇹 Portuguese</option>
            <option value="zh">🇨🇳 Chinese</option>
            <option value="ja">🇯🇵 Japanese</option>
          </select>
        </div>
      </div>

      {/* Text Input */}
      <div className="mb-6">
        <div className="flex justify-between items-center mb-2">
          <label className="text-sm font-medium text-slate-300">Paste your AI text</label>
          <span className={`text-xs font-mono ${charPercent > 90 ? 'text-red-400' : 'text-slate-500'}`}>
            {text.length.toLocaleString()} / 10,000
          </span>
        </div>
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value.slice(0, 10000))}
          placeholder="Paste your AI-generated text here and watch it transform into natural, human-like writing..."
          maxLength="10000"
          rows="8"
          id="text-input"
          className="w-full px-4 py-3 rounded-xl bg-slate-800/80 border border-slate-600/50 text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500/50 transition-smooth resize-y min-h-[120px]"
        />
        {/* Progress bar */}
        <div className="mt-2 w-full h-1 rounded-full bg-slate-700/50 overflow-hidden">
          <div
            className="h-full rounded-full transition-all duration-300"
            style={{
              width: `${charPercent}%`,
              background: charPercent > 90
                ? 'linear-gradient(90deg, #ef4444, #f87171)'
                : 'linear-gradient(90deg, #6366f1, #06b6d4)'
            }}
          />
        </div>
      </div>

      {/* File Upload */}
      <div className="mb-8">
        <label className="block text-sm font-medium text-slate-300 mb-2">Or upload a file</label>
        <label
          className="flex items-center justify-center gap-2 w-full py-3 rounded-xl border-2 border-dashed border-slate-600/50 bg-slate-800/30 text-slate-400 cursor-pointer hover:border-indigo-500/50 hover:text-indigo-300 hover:bg-indigo-500/5 transition-smooth"
          id="file-upload-zone"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
          <span className="text-sm">Drop PDF, DOCX, or TXT file here</span>
          <input
            type="file"
            accept=".pdf,.docx,.txt"
            onChange={handleFileUpload}
            className="hidden"
          />
        </label>
      </div>

      {/* Submit Button */}
      <button
        type="submit"
        disabled={loading || !text.trim()}
        id="humanize-button"
        className="w-full py-4 rounded-xl font-semibold text-white transition-smooth disabled:opacity-40 disabled:cursor-not-allowed relative overflow-hidden group"
        style={{
          background: loading || !text.trim()
            ? '#475569'
            : 'linear-gradient(135deg, #6366f1, #06b6d4)'
        }}
      >
        <span className="relative z-10 flex items-center justify-center gap-2">
          {loading ? (
            <>
              <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
              Processing...
            </>
          ) : (
            <>
              <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              Humanize Text
            </>
          )}
        </span>
        {/* Hover glow */}
        {!loading && text.trim() && (
          <div className="absolute inset-0 bg-white/10 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
        )}
      </button>
    </form>
  )
}
