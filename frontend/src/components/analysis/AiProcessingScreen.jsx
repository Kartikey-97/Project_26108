import React, { useState, useEffect } from 'react';
import { CheckCircle2, Loader2, Terminal, ShieldCheck } from 'lucide-react';

const PIPELINE_STEPS = [
  { id: 1, label: 'Specification Received & Text Parsed', detail: 'Tokenizing parameters, electrical ratings, and environmental clauses.' },
  { id: 2, label: 'Technical Requirements Extracted', detail: 'Identified 7 parameters (Wattage, Efficacy, IP Rating, SPD, THD, CCT).' },
  { id: 3, label: 'Product Category & Domain Mapped', detail: 'Category: Electrical & Lighting | Domain: Highway Infrastructure.' },
  { id: 4, label: 'BIS Database & QCO Mandates Queried', detail: 'Matching against 384 active Indian Standards and DPIIT QCO orders.' },
  { id: 5, label: 'Applicable Standards Ranked', detail: 'Ranking standards by clause coverage and Quality Control Order mandates.' },
  { id: 6, label: 'Completeness Scorecard Generated', detail: 'Auditing tender completeness and detecting missing material clauses.' }
];

export default function AiProcessingScreen({ onCompleteProcessing }) {
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [progressPercent, setProgressPercent] = useState(15);
  const [logs, setLogs] = useState([
    '[SYSTEM] Initializing BIS Recommendation Engine v2.4...',
    '[PIPELINE] Parsing tender specification input string...'
  ]);

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentStepIndex((prev) => {
        if (prev < PIPELINE_STEPS.length - 1) {
          const nextIndex = prev + 1;
          const nextPercent = Math.round(((nextIndex + 1) / PIPELINE_STEPS.length) * 100);
          setProgressPercent(nextPercent);
          
          setLogs((prevLogs) => [
            ...prevLogs,
            `[EXECUTION] Completed Stage ${nextIndex}: ${PIPELINE_STEPS[nextIndex].label}`,
            `[INFO] ${PIPELINE_STEPS[nextIndex].detail}`
          ]);

          return nextIndex;
        } else {
          clearInterval(timer);
          setTimeout(() => {
            if (onCompleteProcessing) onCompleteProcessing();
          }, 800);
          return prev;
        }
      });
    }, 1200);

    return () => clearInterval(timer);
  }, [onCompleteProcessing]);

  return (
    <div className="surface-card p-6 md:p-8 space-y-6 max-w-3xl mx-auto">
      
      {/* Header */}
      <div className="text-center space-y-2 pb-5 border-b" style={{ borderColor: 'var(--border-subtle)' }}>
        <div
          className="inline-flex items-center gap-2 px-3 py-1 rounded text-xs font-semibold border"
          style={{
            backgroundColor: 'var(--brand-tint)',
            borderColor: 'var(--brand-tint-border)',
            color: 'var(--brand-primary)'
          }}
        >
          <ShieldCheck className="w-4 h-4" />
          <span>Technical Analysis Pipeline Running</span>
        </div>
        <h2 className="text-lg font-bold tracking-tight" style={{ color: 'var(--text-main)' }}>
          Identifying Applicable Indian Standards
        </h2>
        <p className="text-xs max-w-md mx-auto" style={{ color: 'var(--text-secondary)' }}>
          Please wait while the engine extracts technical parameters, queries the BIS repository, and audits specification completeness.
        </p>
      </div>

      {/* Progress Bar */}
      <div className="space-y-2">
        <div className="flex items-center justify-between text-xs font-semibold">
          <span style={{ color: 'var(--text-main)' }}>Analysis Progress</span>
          <span className="font-mono" style={{ color: 'var(--brand-primary)' }}>{progressPercent}%</span>
        </div>
        <div
          className="w-full h-2 rounded overflow-hidden border"
          style={{
            backgroundColor: 'var(--bg-surface-secondary)',
            borderColor: 'var(--border-subtle)'
          }}
        >
          <div
            className="h-full rounded transition-all duration-300 ease-out"
            style={{
              width: `${progressPercent}%`,
              backgroundColor: 'var(--brand-primary)'
            }}
          />
        </div>
      </div>

      {/* Pipeline Stages Sequence */}
      <div className="space-y-3 pt-2">
        <span
          className="text-xs font-bold uppercase tracking-wider block"
          style={{ color: 'var(--text-secondary)' }}
        >
          Pipeline Execution Stages
        </span>

        <div className="space-y-2">
          {PIPELINE_STEPS.map((step, idx) => {
            const isFinished = idx < currentStepIndex;
            const isCurrent = idx === currentStepIndex;

            return (
              <div
                key={step.id}
                className="p-3 rounded border text-xs transition-colors flex items-start gap-3"
                style={{
                  backgroundColor: isCurrent
                    ? 'var(--brand-tint)'
                    : isFinished
                    ? 'var(--bg-surface-secondary)'
                    : 'var(--bg-surface)',
                  borderColor: isCurrent
                    ? 'var(--brand-tint-border)'
                    : 'var(--border-subtle)',
                  color: isFinished || isCurrent ? 'var(--text-main)' : 'var(--text-muted)'
                }}
              >
                <div className="shrink-0 mt-0.5">
                  {isFinished ? (
                    <CheckCircle2 className="w-4 h-4" style={{ color: 'var(--status-success-text)' }} />
                  ) : isCurrent ? (
                    <Loader2 className="w-4 h-4 animate-spin" style={{ color: 'var(--brand-primary)' }} />
                  ) : (
                    <div
                      className="w-4 h-4 rounded-full border text-[10px] font-mono flex items-center justify-center"
                      style={{
                        borderColor: 'var(--border-strong)',
                        color: 'var(--text-muted)'
                      }}
                    >
                      {idx + 1}
                    </div>
                  )}
                </div>

                <div className="flex-1 min-w-0">
                  <span className="font-semibold block" style={{ color: 'var(--text-main)' }}>{step.label}</span>
                  {(isFinished || isCurrent) && (
                    <span className="text-[11px] block font-mono mt-0.5" style={{ color: 'var(--text-secondary)' }}>
                      {step.detail}
                    </span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Execution Console Log Container */}
      <div
        className="p-4 rounded border font-mono text-[11px] space-y-1"
        style={{
          backgroundColor: 'var(--bg-surface-secondary)',
          borderColor: 'var(--border-subtle)',
          color: 'var(--text-main)'
        }}
      >
        <div
          className="flex items-center gap-2 pb-2 mb-2 border-b font-bold"
          style={{
            borderColor: 'var(--border-subtle)',
            color: 'var(--text-secondary)'
          }}
        >
          <Terminal className="w-3.5 h-3.5" style={{ color: 'var(--brand-primary)' }} />
          <span>Execution Console Log</span>
        </div>
        <div className="space-y-1 max-h-24 overflow-y-auto">
          {logs.map((log, i) => (
            <p key={i} className="leading-tight">{log}</p>
          ))}
        </div>
      </div>

    </div>
  );
}
