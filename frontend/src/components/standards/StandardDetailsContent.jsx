import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  BookOpen,
  CheckCircle2,
  GitCompare,
  ArrowLeft,
  ShieldAlert,
  Layers,
  FileText,
  Check
} from 'lucide-react';
import { MOCK_STANDARD_DETAIL_SINGLE } from '../../data/mockData';

export default function StandardDetailsContent({ detail = MOCK_STANDARD_DETAIL_SINGLE }) {
  const navigate = useNavigate();
  const [isSelectedCompare, setIsSelectedCompare] = useState(false);

  const handleToggleCompare = () => {
    setIsSelectedCompare(!isSelectedCompare);
  };

  return (
    <div className="space-y-6 animate-fade-in">
      
      {/* Top Action Bar */}
      <div className="flex items-center justify-between">
        <button
          type="button"
          onClick={() => navigate(-1)}
          className="btn-secondary text-xs py-1.5 px-3 flex items-center gap-1.5 cursor-pointer"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to Recommendations</span>
        </button>

        <button
          type="button"
          onClick={handleToggleCompare}
          className="btn-accent text-xs py-2 px-4 flex items-center gap-2 cursor-pointer text-white"
        >
          {isSelectedCompare ? (
            <>
              <Check className="w-4 h-4" />
              <span>Selected for Comparison</span>
            </>
          ) : (
            <>
              <GitCompare className="w-4 h-4" />
              <span>Select for Comparison</span>
            </>
          )}
        </button>
      </div>

      {/* Main Standard Header Card */}
      <div className="surface-card p-6 space-y-4">
        <div
          className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 pb-4 border-b"
          style={{ borderColor: 'var(--border-subtle)' }}
        >
          <div className="flex items-start gap-3.5">
            <div
              className="p-3 rounded border shrink-0 mt-1"
              style={{
                backgroundColor: 'var(--brand-tint)',
                borderColor: 'var(--brand-tint-border)',
                color: 'var(--brand-primary)'
              }}
            >
              <BookOpen className="w-6 h-6" />
            </div>
            <div>
              <div className="flex flex-wrap items-center gap-2 mb-1">
                <h1
                  className="text-xl font-extrabold font-mono"
                  style={{ color: 'var(--text-main)' }}
                >
                  {detail.standardCode}
                </h1>
                <span className="badge badge-current text-xs">{detail.statusBadge}</span>
                {detail.isQcoMandatory && (
                  <span className="badge badge-qco text-xs flex items-center gap-1">
                    <ShieldAlert className="w-3 h-3" />
                    {detail.applicability}
                  </span>
                )}
              </div>
              <h2 className="text-sm font-semibold" style={{ color: 'var(--text-secondary)' }}>
                {detail.standardTitle}
              </h2>
              <p className="text-xs mt-1" style={{ color: 'var(--text-secondary)' }}>
                Category: <span className="font-medium" style={{ color: 'var(--brand-primary)' }}>{detail.category}</span>
              </p>
            </div>
          </div>

          <div className="text-right shrink-0">
            <span className="text-xs block" style={{ color: 'var(--text-secondary)' }}>Current Version</span>
            <span className="text-sm font-bold font-mono" style={{ color: 'var(--status-success-text)' }}>
              {detail.currentVersion}
            </span>
            <span className="text-[11px] block mt-0.5" style={{ color: 'var(--text-muted)' }}>
              {detail.internationalEquivalent}
            </span>
          </div>
        </div>

        {/* Technical Stats Bar */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
          <div
            className="p-3 rounded border"
            style={{
              backgroundColor: 'var(--bg-surface-secondary)',
              borderColor: 'var(--border-subtle)'
            }}
          >
            <span className="block text-[10px] uppercase tracking-wider mb-0.5" style={{ color: 'var(--text-secondary)' }}>Status</span>
            <span className="font-semibold" style={{ color: 'var(--status-success-text)' }}>{detail.statusBadge || 'Active'}</span>
          </div>
          <div
            className="p-3 rounded border"
            style={{
              backgroundColor: 'var(--bg-surface-secondary)',
              borderColor: 'var(--border-subtle)'
            }}
          >
            <span className="block text-[10px] uppercase tracking-wider mb-0.5" style={{ color: 'var(--text-secondary)' }}>QCO Mandate</span>
            <span className="font-semibold" style={{ color: 'var(--brand-primary)' }}>{detail.applicability}</span>
          </div>
          <div
            className="p-3 rounded border"
            style={{
              backgroundColor: 'var(--bg-surface-secondary)',
              borderColor: 'var(--border-subtle)'
            }}
          >
            <span className="block text-[10px] uppercase tracking-wider mb-0.5" style={{ color: 'var(--text-secondary)' }}>International Adoption</span>
            <span className="font-semibold" style={{ color: 'var(--text-main)' }}>{detail.internationalEquivalent}</span>
          </div>
        </div>

        {/* Technical Parameters */}
        <div className="surface-card p-5 space-y-4 mt-6">
          <h3
            className="text-xs font-bold uppercase tracking-wider pb-3 border-b flex items-center gap-2"
            style={{ borderColor: 'var(--border-subtle)', color: 'var(--text-secondary)' }}
          >
            <FileText className="w-4 h-4" style={{ color: 'var(--brand-primary)' }} /> Technical Parameters & Amendments
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs">
            <div>
              <span className="block text-[10px] uppercase tracking-wider mb-1" style={{ color: 'var(--text-secondary)' }}>Operating Voltage</span>
              <span className="font-semibold" style={{ color: 'var(--text-main)' }}>{detail.operatingVoltage}</span>
            </div>
            <div>
              <span className="block text-[10px] uppercase tracking-wider mb-1" style={{ color: 'var(--text-secondary)' }}>IP Rating</span>
              <span className="font-semibold" style={{ color: 'var(--text-main)' }}>{detail.ipRating}</span>
            </div>
            <div>
              <span className="block text-[10px] uppercase tracking-wider mb-1" style={{ color: 'var(--text-secondary)' }}>Test Methods</span>
              <span className="font-semibold" style={{ color: 'var(--text-main)' }}>{detail.testMethods}</span>
            </div>
            <div>
              <span className="block text-[10px] uppercase tracking-wider mb-1" style={{ color: 'var(--text-secondary)' }}>Amendments</span>
              <span className="font-semibold" style={{ color: 'var(--text-main)' }}>
                {detail.amendments?.length > 0 ? detail.amendments.join(', ') : 'None'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Overview & Why Recommended Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* Overview */}
        <div className="surface-card p-5 space-y-3">
          <h3
            className="text-xs font-bold uppercase tracking-wider pb-2 border-b flex items-center gap-2"
            style={{
              borderColor: 'var(--border-subtle)',
              color: 'var(--text-secondary)'
            }}
          >
            <FileText className="w-4 h-4" style={{ color: 'var(--brand-primary)' }} /> Standard Overview &amp; Scope
          </h3>
          <p className="text-xs leading-relaxed font-sans" style={{ color: 'var(--text-main)' }}>
            {detail.overview}
          </p>
        </div>

        {/* Why Recommended */}
        <div className="surface-card p-5 space-y-3">
          <h3
            className="text-xs font-bold uppercase tracking-wider pb-2 border-b flex items-center gap-2"
            style={{
              borderColor: 'var(--border-subtle)',
              color: 'var(--text-secondary)'
            }}
          >
            <CheckCircle2 className="w-4 h-4" style={{ color: 'var(--status-success-text)' }} /> AI Recommendation Reasoning
          </h3>
          <p className="text-xs leading-relaxed font-sans" style={{ color: 'var(--text-main)' }}>
            {detail.whyRecommended}
          </p>
        </div>

      </div>

      {/* Relevant Clauses Table */}
      <div className="surface-card p-5 space-y-4">
        <h3
          className="text-xs font-bold uppercase tracking-wider pb-3 border-b flex items-center gap-2"
          style={{
            borderColor: 'var(--border-subtle)',
            color: 'var(--text-secondary)'
          }}
        >
          <Layers className="w-4 h-4" style={{ color: 'var(--brand-primary)' }} /> Relevant Sections &amp; Clauses
        </h3>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs" style={{ color: 'var(--text-main)' }}>
            <thead
              className="uppercase font-semibold text-[11px] border-b"
              style={{
                backgroundColor: 'var(--bg-surface-secondary)',
                borderColor: 'var(--border-subtle)',
                color: 'var(--text-secondary)'
              }}
            >
              <tr>
                <th className="p-3">Section</th>
                <th className="p-3">Clause Title</th>
                <th className="p-3">Technical Requirements</th>
              </tr>
            </thead>
            <tbody
              className="divide-y font-sans"
              style={{ borderColor: 'var(--border-subtle)' }}
            >
              {detail.relevantSections.map((sec, idx) => (
                <tr key={idx} className="hover:bg-[var(--bg-surface-hover)]">
                  <td className="p-3 font-mono font-bold shrink-0" style={{ color: 'var(--brand-primary)' }}>
                    {sec.section}
                  </td>
                  <td className="p-3 font-semibold max-w-[200px]" style={{ color: 'var(--text-main)' }}>
                    {sec.title}
                  </td>
                  <td className="p-3 leading-relaxed" style={{ color: 'var(--text-secondary)' }}>
                    {sec.details}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
}
