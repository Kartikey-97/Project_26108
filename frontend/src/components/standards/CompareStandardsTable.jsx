import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Check, X, ShieldAlert, Award, ArrowLeft, RotateCcw } from 'lucide-react';

export default function CompareStandardsTable({ initialStandards = [] }) {
  const navigate = useNavigate();
  const [standards, setStandards] = useState(initialStandards);
  useEffect(() => setStandards(initialStandards), [initialStandards]);

  const handleRemoveStandard = (code) => {
    setStandards((prev) => prev.filter((std) => std.standardCode !== code));
  };

  const handleResetComparison = () => {
    setStandards(initialStandards);
  };

  if (standards.length === 0) {
    return (
      <div className="surface-card p-12 text-center space-y-4">
        <h3 className="text-sm font-bold" style={{ color: 'var(--text-main)' }}>
          No Standards Selected for Comparison
        </h3>
        <p className="text-xs max-w-sm mx-auto" style={{ color: 'var(--text-secondary)' }}>
          Please select two or more Indian Standards from the recommendation view to compare technical parameters side-by-side.
        </p>
        <button
          type="button"
          onClick={handleResetComparison}
          className="btn-primary text-xs py-2 px-4 cursor-pointer text-white"
        >
          Reset Comparison Matrix
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in">
      
      {/* Top Header & Reset Actions */}
      <div className="surface-card p-5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-sm font-bold tracking-tight" style={{ color: 'var(--text-main)' }}>
            Side-by-Side Standards Comparison Matrix
          </h2>
          <p className="text-xs mt-0.5" style={{ color: 'var(--text-secondary)' }}>
            Detailed technical comparison across governing clauses, testing standards, and Quality Control Order (QCO) mandates.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={() => navigate(-1)}
            className="btn-secondary text-xs py-1.5 px-3 flex items-center gap-1.5 cursor-pointer"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Back</span>
          </button>

          <button
            type="button"
            onClick={handleResetComparison}
            className="btn-secondary text-xs py-1.5 px-3 flex items-center gap-1.5 cursor-pointer"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Reset Comparison</span>
          </button>
        </div>
      </div>

      {/* Comparison Matrix Table */}
      <div className="surface-card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs" style={{ color: 'var(--text-main)' }}>
            <thead
              className="border-b"
              style={{
                backgroundColor: 'var(--bg-surface-secondary)',
                borderColor: 'var(--border-subtle)'
              }}
            >
              <tr>
                <th
                  className="p-4 w-48 uppercase font-bold text-[11px]"
                  style={{ color: 'var(--text-secondary)' }}
                >
                  Comparison Parameter
                </th>

                {standards.map((std) => (
                  <th
                    key={std.standardCode}
                    className="p-4 min-w-[240px] border-l vertical-top"
                    style={{ borderColor: 'var(--border-subtle)' }}
                  >
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span
                          className="font-mono font-extrabold text-sm"
                          style={{ color: 'var(--text-main)' }}
                        >
                          {std.standardCode}
                        </span>
                        {standards.length > 1 && (
                          <button
                            type="button"
                            onClick={() => handleRemoveStandard(std.standardCode)}
                            className="p-1 rounded hover:opacity-80 transition-opacity"
                            style={{ color: 'var(--text-secondary)' }}
                            title="Remove from comparison"
                          >
                            <X className="w-3.5 h-3.5" />
                          </button>
                        )}
                      </div>

                      <p
                        className="text-[11px] font-normal leading-snug line-clamp-2"
                        style={{ color: 'var(--text-secondary)' }}
                      >
                        {std.standardTitle}
                      </p>

                      <div className="flex items-center gap-2 pt-1">
                        <span className="badge badge-current text-[10px]">{std.statusBadge}</span>
                        {std.isBestMatch && (
                          <span
                            className="text-white text-[10px] font-bold px-2 py-0.5 rounded flex items-center gap-1"
                            style={{ backgroundColor: 'var(--brand-primary)' }}
                          >
                            <Award className="w-3 h-3 text-amber-200" /> Best Match
                          </span>
                        )}
                      </div>
                    </div>
                  </th>
                ))}
              </tr>
            </thead>

            <tbody
              className="divide-y font-sans"
              style={{ borderColor: 'var(--border-subtle)' }}
            >
              
              {/* Row 1: Overall Match Score */}
              <tr className="hover:bg-[var(--bg-surface-hover)]">
                <td
                  className="p-4 font-semibold"
                  style={{
                    backgroundColor: 'var(--bg-surface-secondary)',
                    color: 'var(--text-main)'
                  }}
                >
                  Overall Match Percentage
                </td>
                {standards.map((std) => (
                  <td
                    key={std.standardCode}
                    className="p-4 border-l font-mono font-bold"
                    style={{
                      borderColor: 'var(--border-subtle)',
                      color: 'var(--status-success-text)'
                    }}
                  >
                    {std.matchPercentage}% Match
                  </td>
                ))}
              </tr>

              {/* Row 2: QCO Mandate */}
              <tr className="hover:bg-[var(--bg-surface-hover)]">
                <td
                  className="p-4 font-semibold"
                  style={{
                    backgroundColor: 'var(--bg-surface-secondary)',
                    color: 'var(--text-main)'
                  }}
                >
                  DPIIT QCO Order Mandate
                </td>
                {standards.map((std) => (
                  <td
                    key={std.standardCode}
                    className="p-4 border-l"
                    style={{ borderColor: 'var(--border-subtle)' }}
                  >
                    {std.isQcoMandatory ? (
                      <span className="badge badge-qco text-[10px] flex items-center gap-1">
                        <ShieldAlert className="w-3 h-3" /> Mandatory BIS Certification
                      </span>
                    ) : (
                      <span className="text-xs" style={{ color: 'var(--text-secondary)' }}>
                        Voluntary Standard
                      </span>
                    )}
                  </td>
                ))}
              </tr>

              {/* Row 3: Operating Voltage */}
              <tr className="hover:bg-[var(--bg-surface-hover)]">
                <td
                  className="p-4 font-semibold"
                  style={{
                    backgroundColor: 'var(--bg-surface-secondary)',
                    color: 'var(--text-main)'
                  }}
                >
                  Operating Voltage Range
                </td>
                {standards.map((std) => (
                  <td
                    key={std.standardCode}
                    className="p-4 border-l font-mono"
                    style={{
                      borderColor: 'var(--border-subtle)',
                      color: 'var(--text-main)'
                    }}
                  >
                    {std.operatingVoltage}
                  </td>
                ))}
              </tr>

              {/* Row 4: Ingress Protection Rating */}
              <tr className="hover:bg-[var(--bg-surface-hover)]">
                <td
                  className="p-4 font-semibold"
                  style={{
                    backgroundColor: 'var(--bg-surface-secondary)',
                    color: 'var(--text-main)'
                  }}
                >
                  Ingress Protection (IP Rating)
                </td>
                {standards.map((std) => (
                  <td
                    key={std.standardCode}
                    className="p-4 border-l font-mono font-bold"
                    style={{
                      borderColor: 'var(--border-subtle)',
                      color: 'var(--brand-primary)'
                    }}
                  >
                    {std.ipRating}
                  </td>
                ))}
              </tr>

              {/* Row 5: Surge Protection Device (SPD) */}
              <tr className="hover:bg-[var(--bg-surface-hover)]">
                <td
                  className="p-4 font-semibold"
                  style={{
                    backgroundColor: 'var(--bg-surface-secondary)',
                    color: 'var(--text-main)'
                  }}
                >
                  Surge Protection Device (SPD)
                </td>
                {standards.map((std) => (
                  <td
                    key={std.standardCode}
                    className="p-4 border-l font-mono"
                    style={{
                      borderColor: 'var(--border-subtle)',
                      color: 'var(--text-main)'
                    }}
                  >
                    {std.surgeProtection}
                  </td>
                ))}
              </tr>

              {/* Row 6: Thermal Dissipation & Life */}
              <tr className="hover:bg-[var(--bg-surface-hover)]">
                <td
                  className="p-4 font-semibold"
                  style={{
                    backgroundColor: 'var(--bg-surface-secondary)',
                    color: 'var(--text-main)'
                  }}
                >
                  Thermal Management / Life
                </td>
                {standards.map((std) => (
                  <td
                    key={std.standardCode}
                    className="p-4 border-l"
                    style={{
                      borderColor: 'var(--border-subtle)',
                      color: 'var(--text-secondary)'
                    }}
                  >
                    {std.thermalDissipation}
                  </td>
                ))}
              </tr>

              {/* Row 7: Mandatory Testing Methods */}
              <tr className="hover:bg-[var(--bg-surface-hover)]">
                <td
                  className="p-4 font-semibold"
                  style={{
                    backgroundColor: 'var(--bg-surface-secondary)',
                    color: 'var(--text-main)'
                  }}
                >
                  Governing Test Standard
                </td>
                {standards.map((std) => (
                  <td
                    key={std.standardCode}
                    className="p-4 border-l font-mono font-medium"
                    style={{
                      borderColor: 'var(--border-subtle)',
                      color: 'var(--brand-primary)'
                    }}
                  >
                    {std.testMethods}
                  </td>
                ))}
              </tr>

            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
}
