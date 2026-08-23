import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { CheckCircle2, AlertTriangle, ArrowRight, RotateCcw, Edit2, Check } from 'lucide-react';

export default function ExtractedRequirements({
  summary,
  requirements,
  onReAnalyze
}) {
  const navigate = useNavigate();
  const [reqList, setReqList] = useState(requirements);
  const [editingId, setEditingId] = useState(null);
  const [editValue, setEditValue] = useState('');

  const handleStartEdit = (id, currentVal) => {
    setEditingId(id);
    setEditValue(currentVal);
  };

  const handleSaveEdit = (id) => {
    setReqList((prev) =>
      prev.map((item) => (item.id === id ? { ...item, specifiedValue: editValue } : item))
    );
    setEditingId(null);
  };

  const handleToggleStatus = (id) => {
    setReqList((prev) =>
      prev.map((item) => {
        if (item.id === id) {
          const nextStatus = item.status === 'VALID' ? 'RESTRICTIVE_FLAG' : 'VALID';
          return { ...item, status: nextStatus };
        }
        return item;
      })
    );
  };

  return (
    <div className="space-y-6 animate-fade-in">
      
      {/* Header Bar */}
      <div className="surface-card p-6 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold tracking-tight" style={{ color: 'var(--text-main)' }}>
            Extracted Technical Parameters &amp; Verification
          </h2>
          <p className="text-xs mt-1 max-w-2xl" style={{ color: 'var(--text-secondary)' }}>
            Review and verify the 7 extracted parameters from your draft procurement specification. Edit values inline if adjustments are required before standard mapping.
          </p>
        </div>

        <div className="flex items-center gap-3 shrink-0">
          <button
            type="button"
            onClick={onReAnalyze}
            className="btn-secondary text-xs py-2 px-3 flex items-center gap-1.5 cursor-pointer"
          >
            <RotateCcw className="w-3.5 h-3.5" style={{ color: 'var(--text-secondary)' }} />
            <span>Re-Analyze Spec</span>
          </button>

          <button
            type="button"
            onClick={() => navigate('/recommendations')}
            className="btn-accent text-xs py-2.5 px-4 flex items-center gap-2 cursor-pointer text-white"
          >
            <span>View BIS Recommendations</span>
            <ArrowRight className="w-4 h-4 text-white" />
          </button>
        </div>
      </div>

      {/* Summary Product Metadata Card */}
      <div className="surface-card p-6 space-y-4">
        <h3
          className="text-xs font-bold uppercase tracking-wider pb-2 border-b"
          style={{
            borderColor: 'var(--border-subtle)',
            color: 'var(--text-secondary)'
          }}
        >
          Product Classification &amp; Context Overview
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-xs">
          <div
            className="p-3 rounded border"
            style={{
              backgroundColor: 'var(--bg-surface-secondary)',
              borderColor: 'var(--border-subtle)'
            }}
          >
            <span className="block text-[11px] mb-0.5" style={{ color: 'var(--text-secondary)' }}>Identified Product</span>
            <span className="font-bold" style={{ color: 'var(--text-main)' }}>{summary.product}</span>
          </div>
          <div
            className="p-3 rounded border"
            style={{
              backgroundColor: 'var(--bg-surface-secondary)',
              borderColor: 'var(--border-subtle)'
            }}
          >
            <span className="block text-[11px] mb-0.5" style={{ color: 'var(--text-secondary)' }}>Product Category</span>
            <span className="font-bold" style={{ color: 'var(--brand-primary)' }}>{summary.category}</span>
          </div>
          <div
            className="p-3 rounded border"
            style={{
              backgroundColor: 'var(--bg-surface-secondary)',
              borderColor: 'var(--border-subtle)'
            }}
          >
            <span className="block text-[11px] mb-0.5" style={{ color: 'var(--text-secondary)' }}>Housing Material Grade</span>
            <span className="font-medium" style={{ color: 'var(--text-main)' }}>{summary.material}</span>
          </div>
          <div
            className="p-3 rounded border"
            style={{
              backgroundColor: 'var(--bg-surface-secondary)',
              borderColor: 'var(--border-subtle)'
            }}
          >
            <span className="block text-[11px] mb-0.5" style={{ color: 'var(--text-secondary)' }}>Target Application</span>
            <span className="font-medium" style={{ color: 'var(--text-main)' }}>{summary.application}</span>
          </div>
        </div>
      </div>

      {/* Extracted Parameters Table */}
      <div className="surface-card p-6 space-y-4">
        <div
          className="flex items-center justify-between pb-3 border-b"
          style={{ borderColor: 'var(--border-subtle)' }}
        >
          <h3 className="text-xs font-bold uppercase tracking-wider" style={{ color: 'var(--text-main)' }}>
            Extracted Specification Parameters ({reqList.length})
          </h3>
          <span className="text-xs font-mono" style={{ color: 'var(--text-secondary)' }}>
            Click edit icon to modify extracted values
          </span>
        </div>

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
                <th className="p-3">Type</th>
                <th className="p-3">Specification Parameter</th>
                <th className="p-3">Extracted Tender Value</th>
                <th className="p-3">Governing Standard</th>
                <th className="p-3">Confidence</th>
                <th className="p-3">Status</th>
                <th className="p-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody
              className="divide-y font-sans"
              style={{ borderColor: 'var(--border-subtle)' }}
            >
              {reqList.map((item) => (
                <tr
                  key={item.id}
                  className="transition-colors hover:bg-[var(--bg-surface-hover)]"
                >
                  
                  {/* Type */}
                  <td className="p-3">
                    <span
                      className="font-mono text-[10px] font-bold px-2 py-0.5 rounded border"
                      style={{
                        backgroundColor: 'var(--brand-tint)',
                        borderColor: 'var(--brand-tint-border)',
                        color: 'var(--brand-primary)'
                      }}
                    >
                      {item.type}
                    </span>
                  </td>

                  {/* Parameter Name */}
                  <td className="p-3 font-bold max-w-[180px]" style={{ color: 'var(--text-main)' }}>
                    {item.parameter}
                  </td>

                  {/* Specified Value (Editable) */}
                  <td className="p-3 max-w-xs font-mono">
                    {editingId === item.id ? (
                      <div className="flex items-center gap-1.5">
                        <input
                          type="text"
                          value={editValue}
                          onChange={(e) => setEditValue(e.target.value)}
                          className="rounded px-2 py-1 text-xs focus:outline-none w-full font-mono"
                          style={{
                            backgroundColor: 'var(--input-bg)',
                            borderColor: 'var(--brand-primary)',
                            borderWidth: '1px',
                            color: 'var(--text-main)'
                          }}
                        />
                        <button
                          type="button"
                          onClick={() => handleSaveEdit(item.id)}
                          className="p-1 rounded cursor-pointer text-white"
                          style={{ backgroundColor: 'var(--brand-primary)' }}
                        >
                          <Check className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    ) : (
                      <span className="font-medium" style={{ color: 'var(--status-success-text)' }}>
                        {item.specifiedValue}
                      </span>
                    )}
                  </td>

                  {/* Governing Standard */}
                  <td className="p-3 font-mono font-semibold" style={{ color: 'var(--brand-primary)' }}>
                    {item.governingStandard}
                  </td>

                  {/* Confidence */}
                  <td className="p-3 font-mono" style={{ color: 'var(--text-secondary)' }}>
                    {(item.confidence * 100).toFixed(0)}%
                  </td>

                  {/* Status */}
                  <td className="p-3">
                    {item.status === 'VALID' ? (
                      <span className="badge badge-current text-[10px]">
                        <CheckCircle2 className="w-3 h-3" /> Verified
                      </span>
                    ) : (
                      <span className="badge badge-restrictive text-[10px]">
                        <AlertTriangle className="w-3 h-3" /> Restrictive Clause
                      </span>
                    )}
                  </td>

                  {/* Actions */}
                  <td className="p-3 text-right">
                    <div className="flex items-center justify-end gap-2">
                      <button
                        type="button"
                        onClick={() => handleStartEdit(item.id, item.specifiedValue)}
                        className="btn-secondary p-1.5"
                        title="Edit Parameter Value"
                      >
                        <Edit2 className="w-3.5 h-3.5" />
                      </button>
                      <button
                        type="button"
                        onClick={() => handleToggleStatus(item.id)}
                        className="btn-secondary text-[10px] py-1 px-2"
                      >
                        Toggle Status
                      </button>
                    </div>
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
