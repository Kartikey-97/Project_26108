import React from 'react';
import { ShieldCheck, Cpu, Layers, RefreshCw, FileCheck2 } from 'lucide-react';

export default function Header({ useLiveBackend, setUseLiveBackend, activeCategory, setActiveCategory, isAnalyzing }) {
  return (
    <header className="glass-panel border-b border-slate-800/80 px-6 py-4 mb-6 sticky top-0 z-40">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
        
        {/* Brand & Project Identity */}
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-gradient-to-tr from-indigo-600 to-indigo-400 shadow-lg shadow-indigo-500/20 text-white">
            <ShieldCheck className="w-7 h-7" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold tracking-tight text-white">ProcureIntel AI</h1>
              <span className="badge badge-qco text-xs">SIH 2026 PS 26108</span>
            </div>
            <p className="text-xs text-slate-400">
              Unified Procurement Intelligence Layer & Standards Justification Engine
            </p>
          </div>
        </div>

        {/* System & PoC Controls */}
        <div className="flex flex-wrap items-center gap-3">
          
          {/* Active Proof-of-Concept Category Selector */}
          <div className="flex items-center gap-2 bg-slate-900/90 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-300">
            <Layers className="w-4 h-4 text-indigo-400" />
            <span className="text-slate-400">PoC Domain:</span>
            <select
              value={activeCategory}
              onChange={(e) => setActiveCategory(e.target.value)}
              className="bg-transparent font-medium text-white outline-none cursor-pointer"
            >
              <option value="LED Street Lighting" className="bg-slate-900 text-white">LED Street Lighting (Active PoC)</option>
              <option value="Solar Water Pumps" className="bg-slate-900 text-slate-400" disabled>Solar Water Pumps (Phase 2)</option>
              <option value="Transformers" className="bg-slate-900 text-slate-400" disabled>Power Transformers (Phase 2)</option>
            </select>
          </div>

          {/* Backend API Mode Toggle */}
          <div className="flex items-center gap-2 bg-slate-900/90 border border-slate-800 rounded-lg px-3 py-1.5 text-xs">
            <Cpu className={`w-4 h-4 ${useLiveBackend ? 'text-emerald-400' : 'text-amber-400'}`} />
            <span className="text-slate-400">Mode:</span>
            <button
              type="button"
              onClick={() => setUseLiveBackend(!useLiveBackend)}
              className="font-medium text-white flex items-center gap-1 hover:underline cursor-pointer"
            >
              {useLiveBackend ? (
                <span className="text-emerald-400 flex items-center gap-1">
                  Live API <span className="pulse-dot inline-block ml-1"></span>
                </span>
              ) : (
                <span className="text-amber-400 font-medium">Standalone PoC (Mock Engine)</span>
              )}
            </button>
          </div>

          {/* Verification Badge */}
          <div className="hidden lg:flex items-center gap-1.5 text-xs text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-3 py-1.5 rounded-lg">
            <FileCheck2 className="w-3.5 h-3.5" />
            <span>BIS Source-Grounded</span>
          </div>

        </div>

      </div>
    </header>
  );
}
