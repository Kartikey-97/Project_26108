import React from 'react';
import { X, FileText, ShieldAlert, History, GitFork, CheckCircle2 } from 'lucide-react';

export default function StandardDetailModal({ standard, onClose }) {
  if (!standard) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 animate-fade-in" style={{ backgroundColor: 'rgba(17, 24, 39, 0.5)', backdropFilter: 'blur(4px)' }}>
      <div className="surface-card w-full max-w-2xl max-h-[85vh] overflow-y-auto shadow-xl p-6 space-y-6">
        
        {/* Header */}
        <div className="flex items-start justify-between border-b border-[#E5E2D9] pb-4">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-[#EDF6F5] border border-[#C0E3DF] text-[#087F73]">
              <FileText className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-lg font-bold text-[#17202A] font-mono">{standard.code}</span>
                {standard.status === 'CURRENT' && <span className="badge badge-current">CURRENT</span>}
                {standard.status === 'AMENDED' && <span className="badge badge-amended">AMENDED</span>}
                {standard.status === 'SUPERSEDED' && <span className="badge badge-superseded">SUPERSEDED</span>}
              </div>
              <h3 className="text-xs text-[#667085] font-medium mt-0.5">{standard.title}</h3>
            </div>
          </div>

          <button
            type="button"
            onClick={onClose}
            className="p-1.5 rounded-lg bg-[#F7F6F1] border border-[#E5E2D9] text-[#667085] hover:text-[#17202A] hover:bg-[#E5E2D9] transition-all cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Overview Stats */}
        <div className="grid grid-cols-2 gap-3 text-xs">
          <div className="bg-[#F7F6F1] p-3 rounded-lg border border-[#E5E2D9]">
            <span className="text-[#667085] block mb-0.5">Current Revision:</span>
            <span className="font-semibold text-[#17202A] font-mono">{standard.current_version}</span>
          </div>
          <div className="bg-[#F7F6F1] p-3 rounded-lg border border-[#E5E2D9]">
            <span className="text-[#667085] block mb-0.5">International Adoption:</span>
            <span className="font-semibold text-[#087F73] font-mono">{standard.international_equivalent || 'N/A'}</span>
          </div>
        </div>

        {/* Quality Control Order (QCO) Details */}
        {standard.qco_details && (
          <div className="p-4 rounded-lg bg-[#EDF6F5] border border-[#C0E3DF] text-xs space-y-2">
            <div className="flex items-center gap-2 font-bold text-[#087F73]">
              <ShieldAlert className="w-4 h-4 text-[#087F73]" />
              <span>{standard.qco_details.order_name}</span>
            </div>
            <p className="text-[#17202A]">
              Issued by <span className="font-medium">{standard.qco_details.issuing_authority}</span> (Effective Date: {standard.qco_details.effective_date})
            </p>
            <div className="inline-flex items-center gap-1.5 text-[#2E6B5B] font-semibold bg-[#EBF4F1] px-2.5 py-1 rounded border border-[#C4E2DA]">
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>Mandatory BIS CRS Registration Required</span>
            </div>
          </div>
        )}

        {/* Amendments */}
        <div className="space-y-2">
          <h4 className="text-xs font-semibold text-[#A8752B] uppercase tracking-wider flex items-center gap-1.5">
            <History className="w-3.5 h-3.5" />
            Amendments & Corrigenda
          </h4>
          {standard.amendments && standard.amendments.length > 0 ? (
            <div className="space-y-2">
              {standard.amendments.map((amd, idx) => (
                <div key={idx} className="p-3 rounded-lg bg-[#FDF7ED] border border-[#F6E2C3] text-xs">
                  <div className="flex items-center justify-between text-[#A8752B] font-semibold mb-1">
                    <span>{amd.code}</span>
                    <span className="font-mono text-[#667085]">{amd.year}</span>
                  </div>
                  <p className="text-[#17202A]">{amd.description}</p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-[#9BA3AF] italic">No amendments registered.</p>
          )}
        </div>

        {/* Normative References */}
        <div className="space-y-2">
          <h4 className="text-xs font-semibold text-[#087F73] uppercase tracking-wider flex items-center gap-1.5">
            <GitFork className="w-3.5 h-3.5" />
            Normative Cross References
          </h4>
          {standard.normative_references && standard.normative_references.length > 0 ? (
            <div className="space-y-1.5">
              {standard.normative_references.map((ref, idx) => (
                <div key={idx} className="p-2.5 rounded-lg bg-[#F7F6F1] border border-[#E5E2D9] text-xs text-[#17202A]">
                  {ref}
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-[#9BA3AF] italic">No normative references listed.</p>
          )}
        </div>

        {/* Footer */}
        <div className="pt-4 border-t border-[#E5E2D9] flex items-center justify-between">
          <span className="text-xs text-[#9BA3AF]">Source: BIS Know Your Standard Portal</span>
          <button
            type="button"
            onClick={onClose}
            className="btn-secondary text-xs"
          >
            Close Inspector
          </button>
        </div>

      </div>
    </div>
  );
}
