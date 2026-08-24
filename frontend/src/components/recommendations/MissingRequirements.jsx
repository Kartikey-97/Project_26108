import React, { useState } from 'react';
import { AlertCircle, CheckCircle2, Plus, Copy, Check } from 'lucide-react';

export default function MissingRequirements({ missingList = [] }) {
  const [copiedId, setCopiedId] = useState(null);
  const [appliedIds, setAppliedIds] = useState([]);

  const handleCopyClause = (id, text) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleApplyClause = (id) => {
    setAppliedIds((prev) =>
      prev.includes(id) ? prev.filter((i) => i !== id) : [...prev, id]
    );
  };

  return (
    <div className="space-y-6 animate-fade-in">
      
      {/* Header Banner */}
      <div className="surface-card p-5">
        <h2 className="text-sm font-bold tracking-tight" style={{ color: 'var(--text-main)' }}>
          Specification Completeness Advisory
        </h2>
        <p className="text-xs mt-0.5" style={{ color: 'var(--text-secondary)' }}>
          Consider appending the following standard parameters before finalizing your tender specification to eliminate ambiguity during quality audits.
        </p>
      </div>

      {/* Missing Items Advisory List */}
      <div className="space-y-4">
        {missingList.map((item) => {
          const isApplied = appliedIds.includes(item.id);
          const isCopied = copiedId === item.id;

          return (
            <div
              key={item.id}
              className="surface-card p-5 transition-colors"
              style={isApplied ? {
                borderColor: 'var(--status-success-border)',
                backgroundColor: 'var(--status-success-bg)'
              } : {}}
            >
              {/* Header */}
              <div
                className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-3 border-b"
                style={{ borderColor: 'var(--border-subtle)' }}
              >
                <div className="flex items-center gap-3">
                  <div
                    className="p-2 rounded border"
                    style={{
                      backgroundColor: 'var(--status-warning-bg)',
                      borderColor: 'var(--status-warning-border)',
                      color: 'var(--status-warning-text)'
                    }}
                  >
                    <AlertCircle className="w-4 h-4" />
                  </div>
                  <div>
                    <h3 className="text-sm font-bold" style={{ color: 'var(--text-main)' }}>{item.parameter}</h3>
                    <span className="text-[11px] font-mono" style={{ color: 'var(--text-secondary)' }}>
                      Category: {item.category}
                    </span>
                  </div>
                </div>

                {isApplied && (
                  <span className="badge badge-current text-xs">
                    <CheckCircle2 className="w-3.5 h-3.5" /> Appended to Draft Spec
                  </span>
                )}
              </div>

              {/* Advisory Details & Recommended Clause */}
              <div className="py-3 space-y-3">
                <p className="text-xs leading-relaxed font-sans" style={{ color: 'var(--text-main)' }}>
                  <span className="font-semibold" style={{ color: 'var(--text-main)' }}>Advisory: </span>
                  {item.missingExplanation}
                </p>

                {/* Standard Clause Box */}
                <div
                  className="p-3.5 rounded border space-y-2"
                  style={{
                    backgroundColor: 'var(--bg-surface-secondary)',
                    borderColor: 'var(--border-subtle)'
                  }}
                >
                  <div className="flex items-center justify-between">
                    <span
                      className="text-[11px] font-semibold uppercase tracking-wider"
                      style={{ color: 'var(--brand-primary)' }}
                    >
                      Recommended Standard Clause:
                    </span>
                    <button
                      type="button"
                      onClick={() => handleCopyClause(item.id, item.suggestedClauseText)}
                      className="text-[11px] font-medium flex items-center gap-1 cursor-pointer"
                      style={{ color: 'var(--text-secondary)' }}
                    >
                      {isCopied ? (
                        <Check className="w-3.5 h-3.5" style={{ color: 'var(--status-success-text)' }} />
                      ) : (
                        <Copy className="w-3.5 h-3.5" />
                      )}
                      <span>{isCopied ? 'Copied!' : 'Copy Clause'}</span>
                    </button>
                  </div>

                  <p
                    className="text-xs font-mono p-3 rounded border leading-relaxed"
                    style={{
                      backgroundColor: 'var(--bg-surface)',
                      borderColor: 'var(--border-subtle)',
                      color: 'var(--text-main)'
                    }}
                  >
                    "{item.suggestedClauseText}"
                  </p>
                </div>
              </div>

              {/* Action Button */}
              <div
                className="pt-3 border-t flex items-center justify-between"
                style={{ borderColor: 'var(--border-subtle)' }}
              >
                <span className="text-[11px] font-mono" style={{ color: 'var(--text-secondary)' }}>
                  Governing BIS standard checklist
                </span>
                
                <button
                  type="button"
                  onClick={() => handleApplyClause(item.id)}
                  className={`btn-primary text-xs py-1.5 px-3 flex items-center gap-1.5 cursor-pointer ${
                    isApplied ? 'opacity-90' : ''
                  }`}
                >
                  {isApplied ? (
                    <>
                      <Check className="w-3.5 h-3.5" />
                      <span>Clause Included</span>
                    </>
                  ) : (
                    <>
                      <Plus className="w-3.5 h-3.5" />
                      <span>Append to Specification</span>
                    </>
                  )}
                </button>
              </div>

            </div>
          );
        })}
        {missingList.length === 0 && (
          <div
            className="surface-card p-6 text-center text-xs"
            style={{ color: 'var(--text-secondary)' }}
          >
            <CheckCircle2
              className="w-5 h-5 mx-auto mb-2"
              style={{ color: 'var(--status-success-text)' }}
            />
            No missing specification parameters were flagged for this analysis.
          </div>
        )}
      </div>

    </div>
  );
}
