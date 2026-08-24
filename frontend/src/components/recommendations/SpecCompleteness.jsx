import React from 'react';
import {
  CheckCircle2,
  AlertCircle,
  ShieldCheck,
  BarChart3
} from 'lucide-react';
import { MOCK_COMPLETENESS_DATA } from '../../data/mockData';

export default function SpecCompleteness({ completeness = MOCK_COMPLETENESS_DATA }) {
  return (
    <div className="space-y-6 animate-fade-in">
      
      {/* Header Banner */}
      <div className="surface-card p-5">
        <h2 className="text-sm font-bold tracking-tight" style={{ color: 'var(--text-main)' }}>
          Specification Completeness Scorecard
        </h2>
        <p className="text-xs mt-0.5" style={{ color: 'var(--text-secondary)' }}>
          Multi-dimensional completeness scorecard evaluating technical completeness, safety coverage, material standards, and legal QCO compliance.
        </p>
      </div>

      {/* Top Gauge Overview & Grade Card */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
        
        {/* Overall Score Circle Card */}
        <div className="md:col-span-5 surface-card p-6 text-center flex flex-col items-center justify-center space-y-4">
          <span
            className="text-xs font-bold uppercase tracking-wider"
            style={{ color: 'var(--text-secondary)' }}
          >
            Overall Specification Quality Score
          </span>

          <div className="relative flex items-center justify-center">
            <div
              className="w-36 h-36 rounded-full border-8 flex items-center justify-center"
              style={{
                borderColor: 'var(--bg-surface-secondary)',
                borderTopColor: 'var(--brand-primary)',
                borderRightColor: 'var(--status-success-text)'
              }}
            >
              <div className="text-center">
                <span className="text-4xl font-extrabold font-mono" style={{ color: 'var(--text-main)' }}>
                  {completeness.overallScore}%
                </span>
                <span className="text-xs font-bold block mt-0.5" style={{ color: 'var(--status-success-text)' }}>
                  Grade {completeness.grade}
                </span>
              </div>
            </div>
          </div>

          <div className="space-y-1">
            <h3 className="text-sm font-bold" style={{ color: 'var(--text-main)' }}>{completeness.statusText}</h3>
            <p className="text-xs leading-relaxed max-w-xs mx-auto" style={{ color: 'var(--text-secondary)' }}>
              {completeness.summaryText}
            </p>
          </div>
        </div>

        {/* Category-Wise Progress Bars */}
        <div className="md:col-span-7 surface-card p-6 space-y-5">
          <div
            className="flex items-center justify-between pb-3 border-b"
            style={{ borderColor: 'var(--border-subtle)' }}
          >
            <h3 className="text-sm font-bold flex items-center gap-2" style={{ color: 'var(--text-main)' }}>
              <BarChart3 className="w-4 h-4" style={{ color: 'var(--brand-primary)' }} />
              Category-Wise Completeness Breakdown
            </h3>
            <span className="text-xs font-mono" style={{ color: 'var(--text-secondary)' }}>
              4 Subsystems Audited
            </span>
          </div>

          <div className="space-y-4">
            {completeness.categoryScores.map((cat, idx) => (
              <div key={idx} className="space-y-1.5">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-semibold" style={{ color: 'var(--text-main)' }}>{cat.name}</span>
                  <span className="font-bold font-mono" style={{ color: 'var(--text-main)' }}>{cat.score}%</span>
                </div>

                <div
                  className="w-full h-2 rounded overflow-hidden border"
                  style={{
                    backgroundColor: 'var(--bg-surface-secondary)',
                    borderColor: 'var(--border-subtle)'
                  }}
                >
                  <div
                    className="h-full rounded"
                    style={{
                      width: `${cat.score}%`,
                      backgroundColor:
                        cat.score >= 90
                          ? 'var(--brand-primary)'
                          : cat.score >= 80
                          ? 'var(--brand-primary)'
                          : 'var(--status-warning-text)'
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

      </div>

      {/* Strengths vs. Areas for Improvement */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* Specification Strengths */}
        <div className="surface-card p-5 space-y-3">
          <div
            className="flex items-center gap-2.5 pb-3 border-b"
            style={{ borderColor: 'var(--border-subtle)' }}
          >
            <div
              className="p-2 rounded border"
              style={{
                backgroundColor: 'var(--status-success-bg)',
                borderColor: 'var(--status-success-border)',
                color: 'var(--status-success-text)'
              }}
            >
              <ShieldCheck className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-xs font-bold uppercase tracking-wider" style={{ color: 'var(--text-main)' }}>
                Specification Strengths
              </h3>
              <p className="text-[11px] font-medium" style={{ color: 'var(--status-success-text)' }}>
                Fully aligned with Indian Standards (BIS)
              </p>
            </div>
          </div>

          <ul className="space-y-2 text-xs" style={{ color: 'var(--text-main)' }}>
            {completeness.strengths.map((str, idx) => (
              <li
                key={idx}
                className="flex items-start gap-2.5 p-2.5 rounded border"
                style={{
                  backgroundColor: 'var(--bg-surface-secondary)',
                  borderColor: 'var(--border-subtle)'
                }}
              >
                <CheckCircle2 className="w-4 h-4 shrink-0 mt-0.5" style={{ color: 'var(--status-success-text)' }} />
                <span>{str}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Areas for Improvement */}
        <div className="surface-card p-5 space-y-3">
          <div
            className="flex items-center gap-2.5 pb-3 border-b"
            style={{ borderColor: 'var(--border-subtle)' }}
          >
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
              <h3 className="text-xs font-bold uppercase tracking-wider" style={{ color: 'var(--text-main)' }}>
                Areas for Improvement
              </h3>
              <p className="text-[11px] font-medium" style={{ color: 'var(--status-warning-text)' }}>
                Recommended clauses to append
              </p>
            </div>
          </div>

          <ul className="space-y-2 text-xs" style={{ color: 'var(--text-main)' }}>
            {completeness.areasForImprovement.map((imp, idx) => (
              <li
                key={idx}
                className="flex items-start gap-2.5 p-2.5 rounded border"
                style={{
                  backgroundColor: 'var(--bg-surface-secondary)',
                  borderColor: 'var(--border-subtle)'
                }}
              >
                <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" style={{ color: 'var(--status-warning-text)' }} />
                <span>{imp}</span>
              </li>
            ))}
          </ul>
        </div>

      </div>

    </div>
  );
}
