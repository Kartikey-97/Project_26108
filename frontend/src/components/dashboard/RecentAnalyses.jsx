import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowUpRight, CheckCircle2, AlertTriangle, Clock } from 'lucide-react';

export default function RecentAnalyses({ analyses = [] }) {
  const navigate = useNavigate();

  const getStatusBadge = (status) => {
    switch (status) {
      case 'COMPLETED':
        return (
          <span className="badge badge-current text-[10px]">
            <CheckCircle2 className="w-3 h-3" /> Completed
          </span>
        );
      case 'WARNING_FLAGGED':
        return (
          <span className="badge badge-amended text-[10px]">
            <AlertTriangle className="w-3 h-3" /> Flagged Clause
          </span>
        );
      case 'IN_REVIEW':
        return (
          <span className="badge badge-qco text-[10px]">
            <Clock className="w-3 h-3" /> In Review
          </span>
        );
      default:
        return <span className="badge badge-current text-[10px]">{status}</span>;
    }
  };

  return (
    <div className="surface-card space-y-4 p-5">
      <div
        className="flex items-center justify-between pb-3 border-b"
        style={{ borderColor: 'var(--border-subtle)' }}
      >
        <div>
          <h2 className="text-sm font-bold tracking-tight" style={{ color: 'var(--text-main)' }}>
            Recent Procurement Analyses
          </h2>
          <p className="text-xs mt-0.5" style={{ color: 'var(--text-secondary)' }}>
            Operational log of specification audits and BIS standard recommendations.
          </p>
        </div>

        <button
          onClick={() => navigate('/history')}
          className="text-xs font-semibold flex items-center gap-1 cursor-pointer transition-colors"
          style={{ color: 'var(--brand-primary)' }}
        >
          <span>View All History</span>
          <ArrowUpRight className="w-3.5 h-3.5" />
        </button>
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
              <th className="p-3">Analysis Ref / Title</th>
              <th className="p-3">Department</th>
              <th className="p-3">Mapped Standards</th>
              <th className="p-3">Completeness Score</th>
              <th className="p-3">Status</th>
              <th className="p-3 text-right">Action</th>
            </tr>
          </thead>
          <tbody
            className="font-sans divide-y"
            style={{ borderColor: 'var(--border-subtle)' }}
          >
            {analyses.map((item) => (
              <tr
                key={item.id}
                className="transition-colors hover:bg-[var(--bg-surface-hover)]"
              >
                <td className="p-3 max-w-xs">
                  <span className="text-[10px] font-mono block mb-0.5" style={{ color: 'var(--text-muted)' }}>{item.id}</span>
                  <span className="font-semibold truncate block" style={{ color: 'var(--text-main)' }}>{item.title}</span>
                  <span className="text-[11px] block font-medium" style={{ color: 'var(--brand-primary)' }}>{item.category}</span>
                </td>
                <td className="p-3 font-medium" style={{ color: 'var(--text-secondary)' }}>
                  <span className="block truncate max-w-[160px]">{item.department}</span>
                  <span className="text-[10px] font-mono" style={{ color: 'var(--text-muted)' }}>{item.date}</span>
                </td>
                <td className="p-3">
                  <div className="flex items-center gap-1 flex-wrap">
                    <span className="font-mono font-semibold" style={{ color: 'var(--brand-primary)' }}>
                      {item.standardsCount} Standards
                    </span>
                    {item.qcoMandatory && (
                      <span className="badge badge-qco text-[9px]">
                        QCO
                      </span>
                    )}
                  </div>
                  <p className="text-[10px] font-mono truncate max-w-[160px] mt-0.5" style={{ color: 'var(--text-secondary)' }}>
                    {(item.standards || []).join(', ')}
                  </p>
                </td>
                <td className="p-3">
                  <div className="flex items-center gap-2">
                    <span className="font-bold font-mono" style={{ color: 'var(--text-main)' }}>
                      {item.completenessScore}%
                    </span>
                    <div
                      className="w-16 h-1.5 rounded-full overflow-hidden"
                      style={{ backgroundColor: 'var(--border-subtle)' }}
                    >
                      <div
                        className="h-full rounded-full"
                        style={{
                          width: `${item.completenessScore}%`,
                          backgroundColor:
                            item.completenessScore >= 90
                              ? 'var(--brand-primary)'
                              : item.completenessScore >= 80
                              ? 'var(--brand-primary)'
                              : 'var(--status-warning-text)'
                        }}
                      />
                    </div>
                  </div>
                </td>
                <td className="p-3">
                  {getStatusBadge(item.status)}
                </td>
                <td className="p-3 text-right">
                  <button
                    onClick={() => navigate(`/recommendations?analysis=${item.id}`)}
                    className="btn-secondary text-[11px] py-1 px-2.5"
                  >
                    Inspect Report
                  </button>
                </td>
              </tr>
            ))}
            {analyses.length === 0 && (
              <tr>
                <td
                  colSpan={6}
                  className="p-6 text-center text-xs"
                  style={{ color: 'var(--text-secondary)' }}
                >
                  No analyses yet. Run a specification audit to see results here.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
