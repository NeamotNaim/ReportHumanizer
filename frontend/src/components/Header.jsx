export default function Header({ providerInfo }) {
  const providerLabel = {
    gemini: '✨ Gemini',
    openai: '🤖 GPT-4o',
    anthropic: '🧠 Claude',
  }

  return (
    <header className="glass sticky top-0 z-50 border-b border-indigo-500/10">
      <div className="max-w-5xl mx-auto px-4 py-4 flex justify-between items-center">
        <div className="flex items-center gap-3">
          {/* Logo icon */}
          <div className="w-10 h-10 rounded-xl animated-gradient flex items-center justify-center shadow-lg">
            <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
            </svg>
          </div>
          <div>
            <h1 className="text-xl font-bold gradient-text">Draft Revision Studio</h1>
            <p className="text-xs text-slate-400">Multi-stage AI humanization pipeline</p>
          </div>
        </div>

        {/* Provider status badge */}
        {providerInfo && (
          <div className="flex items-center gap-2">
            <span className={`w-2 h-2 rounded-full ${providerInfo.llm_available ? 'bg-emerald-400 shadow-[0_0_6px_rgba(16,185,129,0.5)]' : 'bg-red-400'}`} />
            <span className="text-xs text-slate-400">
              {providerInfo.llm_available
                ? providerLabel[providerInfo.provider] || providerInfo.provider
                : 'No LLM connected'}
            </span>
          </div>
        )}
      </div>
    </header>
  )
}
