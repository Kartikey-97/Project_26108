import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  GitCompare,
  ExternalLink,
  ShieldAlert,
  Check,
  Award
} from 'lucide-react';
import { MOCK_RECOMMENDED_STANDARDS } from '../../data/mockData';

export default function RecommendedStandards({
  standards = MOCK_RECOMMENDED_STANDARDS,
  onSelectForCompare,
  selectedCompareIds = []
}) {
  const navigate = useNavigate();

  return (
    <div className="space-y-4 animate-fade-in">
      {standards.map((std) => {
        const isSelectedForCompare = selectedCompareIds.includes(std.id);
        const isBestMatch = std.rank === 1;

        return (
          <div
            key={std.id}
            className={`surface-card p-6 border transition-colors ${
              isBestMatch
                ? 'border-l-4'
                : ''
            }`}
            style={{
              borderLeftColor: isBestMatch ? 'var(--brand-primary)' : 'var(--border-subtle)',
              backgroundColor: isBestMatch ? 'var(--brand-tint)' : 'var(--bg-surface)'
            }}
          >
            {/* Header: Rank, Standard Code, Status Badges, Match Score */}
            <div
              className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-4 border-b"
              style={{ borderColor: 'var(--border-subtle)' }}
            >
              <div className="flex items-center gap-3">
                
                {/* Rank Badge */}
                <div
                  className="w-8 h-8 rounded font-mono font-bold text-xs flex items-center justify-center shrink-0 border"
                  style={{
                    backgroundColor: isBestMatch ? 'var(--brand-primary)' : 'var(--bg-surface-secondary)',
                    color: isBestMatch ? '#FFFFFF' : 'var(--text-main)',
                    borderColor: isBestMatch ? 'var(--brand-primary)' : 'var(--border-subtle)'
                  }}
                >
                  #{std.rank}
                </div>

                <div>
                  <div className="flex items-center gap-2 flex-wrap">
                    <h3 className="text-base font-extrabold font-mono" style={{ color: 'var(--text-main)' }}>
                      {std.standardCode}
                    </h3>
                    {isBestMatch && (
                      <span
                        className="text-white text-[10px] font-bold px-2 py-0.5 rounded flex items-center gap-1"
                        style={{ backgroundColor: 'var(--brand-primary)' }}
                      >
                        <Award className="w-3 h-3 text-amber-200" />
                        BEST MATCH
                      </span>
                    )}
                    <span className="badge badge-current text-[10px]">{std.statusBadge}</span>
                    {std.isQcoMandatory && (
                      <span className="badge badge-qco text-[10px] flex items-center gap-1">
                        <ShieldAlert className="w-3 h-3" />
                        {std.applicability}
                      </span>
                    )}
                  </div>
                  <p className="text-xs font-medium mt-0.5" style={{ color: 'var(--text-secondary)' }}>
                    {std.standardTitle}
                  </p>
                </div>

              </div>

              {/* Match Score & Compare Button */}
              <div className="flex items-center gap-4 shrink-0">
                <div className="text-right">
                  <div className="flex items-center justify-end gap-2">
                    <span
                      className="text-xs font-bold font-mono"
                      style={{ color: 'var(--status-success-text)' }}
                    >
                      {std.matchPercentage}% Match
                    </span>
                  </div>
                  <div
                    className="w-24 h-1.5 rounded-full overflow-hidden mt-1"
                    style={{ backgroundColor: 'var(--border-subtle)' }}
                  >
                    <div
                      className="h-full rounded-full"
                      style={{
                        width: `${std.matchPercentage}%`,
                        backgroundColor: 'var(--brand-primary)'
                      }}
                    />
                  </div>
                </div>

                <button
                  type="button"
                  onClick={() => onSelectForCompare(std.id)}
                  className={`btn-secondary text-xs py-1.5 px-3 flex items-center gap-1.5 cursor-pointer ${
                    isSelectedForCompare ? 'font-bold' : ''
                  }`}
                  style={isSelectedForCompare ? {
                    borderColor: 'var(--brand-primary)',
                    color: 'var(--brand-primary)',
                    backgroundColor: 'var(--brand-tint)'
                  } : {}}
                >
                  {isSelectedForCompare ? (
                    <Check className="w-3.5 h-3.5" style={{ color: 'var(--brand-primary)' }} />
                  ) : (
                    <GitCompare className="w-3.5 h-3.5" style={{ color: 'var(--text-secondary)' }} />
                  )}
                  <span>{isSelectedForCompare ? 'Selected' : 'Compare'}</span>
                </button>
              </div>
            </div>

            {/* Body */}
            <div className="py-4 space-y-3">
              <p className="text-xs leading-relaxed font-sans" style={{ color: 'var(--text-main)' }}>
                <span className="font-semibold" style={{ color: 'var(--text-main)' }}>Why it matches: </span>
                {std.aiExplanation}
              </p>

              <div className="flex flex-wrap items-center gap-2 pt-1">
                <span className="text-[11px] font-semibold" style={{ color: 'var(--text-secondary)' }}>Matched Specifications:</span>
                {std.matchedRequirements.map((req, idx) => (
                  <span
                    key={idx}
                    className="badge badge-current text-[11px] font-mono lowercase"
                  >
                    ✓ {req}
                  </span>
                ))}
              </div>
            </div>

            {/* Footer */}
            <div
              className="pt-3 border-t flex items-center justify-between"
              style={{ borderColor: 'var(--border-subtle)' }}
            >
              <span className="text-[11px] font-mono" style={{ color: 'var(--text-secondary)' }}>
                Category: {std.category}
              </span>
              
              <button
                type="button"
                onClick={() => navigate(`/standards/${encodeURIComponent(std.standardCode)}`)}
                className="text-xs font-semibold flex items-center gap-1 cursor-pointer"
                style={{ color: 'var(--brand-primary)' }}
              >
                <span>Inspect Standard Details</span>
                <ExternalLink className="w-3.5 h-3.5" />
              </button>
            </div>

          </div>
        );
      })}
    </div>
  );
}
