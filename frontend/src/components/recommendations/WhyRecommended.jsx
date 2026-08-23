import React from 'react';
import { ArrowRight, FileText, CheckCircle2, ShieldAlert } from 'lucide-react';
import { MOCK_EVIDENCE_MAP } from '../../data/mockData';

export default function WhyRecommended({ evidence = MOCK_EVIDENCE_MAP }) {
  return (
    <div className="space-y-6 animate-fade-in">
      
      {/* Header Banner */}
      <div className="surface-card p-5">
        <h2 className="text-sm font-bold tracking-tight" style={{ color: 'var(--text-main)' }}>
          Evidence-Based Specification Mapping
        </h2>
        <p className="text-xs mt-0.5" style={{ color: 'var(--text-secondary)' }}>
          Verbatim mapping between tender technical parameters and governing Indian Standard clauses (BIS) to ensure 100% audit trail compliance.
        </p>
      </div>

      {/* Evidence Mapping List */}
      <div className="space-y-4">
        {evidence.map((item) => (
          <div key={item.id} className="surface-card p-5 space-y-4">
            
            {/* Top Requirement Header */}
            <div
              className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 pb-3 border-b"
              style={{ borderColor: 'var(--border-subtle)' }}
            >
              <div className="flex items-center gap-2">
                <span
                  className="text-xs font-bold px-2.5 py-0.5 rounded border font-mono"
                  style={{
                    backgroundColor: 'var(--brand-tint)',
                    borderColor: 'var(--brand-tint-border)',
                    color: 'var(--brand-primary)'
                  }}
                >
                  {item.requirement}
                </span>
                <span className="text-xs font-semibold" style={{ color: 'var(--text-main)' }}>
                  "{item.tenderTextSnippet}"
                </span>
              </div>

              <div className="flex items-center gap-2">
                <span className="text-xs font-mono" style={{ color: 'var(--text-secondary)' }}>
                  Confidence: <span className="font-bold" style={{ color: 'var(--status-success-text)' }}>{(item.confidence * 100).toFixed(0)}%</span>
                </span>
                <span className="badge badge-current text-[10px]">
                  <CheckCircle2 className="w-3 h-3" /> Exact Match
                </span>
              </div>
            </div>

            {/* Mapping Grid */}
            <div className="grid grid-cols-1 md:grid-cols-12 gap-4 items-center">
              
              {/* User Tender Spec */}
              <div
                className="md:col-span-5 p-3.5 rounded border space-y-1"
                style={{
                  backgroundColor: 'var(--bg-surface-secondary)',
                  borderColor: 'var(--border-subtle)'
                }}
              >
                <span
                  className="text-[10px] font-bold uppercase tracking-wider block"
                  style={{ color: 'var(--text-secondary)' }}
                >
                  User Tender Requirement
                </span>
                <p className="text-xs font-mono leading-relaxed" style={{ color: 'var(--text-main)' }}>
                  "{item.tenderTextSnippet}"
                </p>
              </div>

              {/* Arrow Connector */}
              <div className="md:col-span-2 flex items-center justify-center">
                <div
                  className="p-2 rounded-full border"
                  style={{
                    backgroundColor: 'var(--brand-tint)',
                    borderColor: 'var(--brand-tint-border)',
                    color: 'var(--brand-primary)'
                  }}
                >
                  <ArrowRight className="w-4 h-4" />
                </div>
              </div>

              {/* Governing Standard Clause */}
              <div
                className="md:col-span-5 p-3.5 rounded border space-y-1"
                style={{
                  backgroundColor: 'var(--brand-tint)',
                  borderColor: 'var(--brand-tint-border)'
                }}
              >
                <div className="flex items-center justify-between">
                  <span
                    className="text-[10px] font-bold uppercase tracking-wider block"
                    style={{ color: 'var(--brand-primary)' }}
                  >
                    Governing BIS Clause
                  </span>
                  <span className="text-[11px] font-mono font-bold" style={{ color: 'var(--brand-primary)' }}>
                    {item.mappedClause}
                  </span>
                </div>
                <p className="text-xs font-mono leading-relaxed" style={{ color: 'var(--text-main)' }}>
                  "{item.standardClauseText}"
                </p>
              </div>

            </div>

            {/* AI Reasoning Footer */}
            <div
              className="pt-2 border-t text-xs leading-relaxed font-sans"
              style={{
                borderColor: 'var(--border-subtle)',
                color: 'var(--text-secondary)'
              }}
            >
              <span className="font-semibold" style={{ color: 'var(--text-main)' }}>AI Justification: </span>
              {item.aiJustification}
            </div>

          </div>
        ))}
      </div>

    </div>
  );
}
