export default function Footer() {
  return (
    <footer className="relative z-10 border-t border-slate-800 mt-16">
      <div className="max-w-5xl mx-auto px-4 py-8 text-center">
        <p className="text-slate-400 text-sm">
          &copy; {new Date().getFullYear()} Draft Revision Studio. Open Source. MIT License.
        </p>
        <p className="text-xs text-slate-500 mt-1">
          Built with React, Vite, Flask, and spaCy
        </p>
      </div>
    </footer>
  )
}
