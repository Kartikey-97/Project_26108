import React, { useState } from 'react';
import { ShieldCheck, FileText, CheckCircle2, AlertTriangle, ExternalLink, Info, Edit3, Save } from 'lucide-react';

export default function EvidenceChainView({ requirements: initialRequirements, onSelectStandard, onUpdateRequirements }) {
  const [requirements, setRequirements] = useState(initialRequirements);
  const [selectedReqId, setSelectedReqId] = useState(initialRequirements[0]?.id || null);
  const [isEditing, setIsEditing] = useState(false);
  const [editValue, setEditValue] = useState('');
  const [editParam, setEditParam] = useState('');

  const selectedReq = requirements.find(r => r.id === selectedReqId) || requirements[0];

  const handleStartEdit = () => {
    if (selectedReq) {
      setEditParam(selectedReq.parameter);
      setEditValue(selectedReq.specified_value);
      setIsEditing(true);
    }
  };

  const handleSaveEdit = () => {
    const updated = requirements.map(r => {
      if (r.id === selectedReqId) {
        return {
          ...r,
          parameter: editParam,
          specified_value: editValue,
          status: 'USER_EDITED',
          compliance_status: 'Modified by Procurement Officer (User Approved)'
        };
      }
      return r;
    });
    setRequirements(updated);
    if (onUpdateRequirements) onUpdateRequirements(updated);
    setIsEditing(false);
  };

  const handleMarkReviewed = (id) => {
    const updated = requirements.map(r => {
      if (r.id === id) {
        return { ...r, is_reviewed: !r.is_reviewed };
      }
      return r;
    });
    setRequirements(updated);
    if (onUpdateRequirements) onUpdateRequirements(updated);
  };

  return (
    <div className="space-y-6 animate-fade-in">
      
      {/* Header Banner */}
      <div className="surface-card p-5 border-l-4 border-l-[#087F73]">
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="badge badge-qco">Core Innovation</span>
              <h2 className="text-base font-bold text-[#17202A]">Extracted Requirements & Provenance Chain</h2>
            </div>
            <p className="text-xs text-[#667085]">
              Review, edit/correct extracted requirements, identify uncertainty, and inspect the evidence chain linking each spec to official Indian Standards (BIS).
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left List: Extracted Requirements (With Edit & Review Status) */}
        <div className="lg:col-span-5 space-y-3">
          <div className="flex items-center justify-between px-1">
            <h3 className="text-xs font-semibold text-[#667085] uppercase tracking-wider">
              Requirements ({requirements.length})
            </h3>
            <span className="text-xs text-[#087F73] font-medium">Click to inspect / edit</span>
          </div>
          
          {requirements.map((req) => {
            const isSelected = req.id === selectedReqId;
            return (
              <div
                key={req.id}
                onClick={() => {
                  setSelectedReqId(req.id);
                  setIsEditing(false);
                }}
                className={`w-full text-left p-4 rounded-lg transition-all cursor-pointer border ${
                  isSelected
                    ? 'bg-[#EDF6F5] border-[#087F73]'
                    : 'bg-white border-[#E5E2D9] hover:border-[#B8D8D6] hover:bg-[#F7F6F1]'
                }`}
              >
                <div className="flex items-start justify-between gap-2 mb-1.5">
                  <span className="text-xs font-medium text-[#667085]">{req.category}</span>
                  <div className="flex items-center gap-1.5">
                    {req.status === 'USER_EDITED' && (
                      <span className="badge bg-[#EDF6F5] text-[#087F73] border-[#C0E3DF] text-[10px]">User Edited</span>
                    )}
                    {req.severity === 'SUCCESS' && (
                      <span className="badge badge-current text-[10px]">Supported</span>
                    )}
                    {req.severity === 'WARNING' && (
                      <span className="badge badge-restrictive text-[10px]">Restrictive</span>
                    )}
                    {req.severity === 'INFO' && (
                      <span className="badge badge-amended text-[10px]">Uncited</span>
                    )}
                  </div>
                </div>

                <h4 className="text-sm font-semibold text-[#17202A] mb-1">{req.parameter}</h4>
                <p className="text-xs font-mono text-[#087F73] font-medium">{req.specified_value}</p>

                <div className="mt-2.5 pt-2 border-t border-[#E5E2D9] flex items-center justify-between text-[11px]">
                  <span className="text-[#667085]">Standard: {req.evidence_chain.standard_code}</span>
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleMarkReviewed(req.id);
                    }}
                    className={`px-2 py-0.5 rounded text-[10px] font-semibold transition-all cursor-pointer ${
                      req.is_reviewed
                        ? 'bg-[#EBF4F1] text-[#2E6B5B] border border-[#C4E2DA]'
                        : 'bg-[#F7F6F1] text-[#667085] border border-[#E5E2D9] hover:text-[#17202A]'
                    }`}
                  >
                    {req.is_reviewed ? '✓ Reviewed' : 'Mark Reviewed'}
                  </button>
                </div>
              </div>
            );
          })}
        </div>

        {/* Right Detail: Evidence Justification & Interactive Requirement Editor */}
        <div className="lg:col-span-7">
          {selectedReq && (
            <div className="surface-card p-6 space-y-6 sticky top-24">
              
              <div className="flex items-center justify-between border-b border-[#E5E2D9] pb-4">
                <div>
                  <span className="text-xs font-semibold text-[#087F73] uppercase tracking-wider">Requirement & Evidence Detail</span>
                  <h3 className="text-base font-bold text-[#17202A] mt-0.5">{selectedReq.parameter}</h3>
                </div>
                
                <div className="flex items-center gap-2">
                  {!isEditing ? (
                    <button
                      type="button"
                      onClick={handleStartEdit}
                      className="btn-secondary text-xs py-1.5 px-3 cursor-pointer"
                    >
                      <Edit3 className="w-3.5 h-3.5" />
                      Edit Requirement
                    </button>
                  ) : (
                    <button
                      type="button"
                      onClick={handleSaveEdit}
                      className="btn-accent text-xs py-1.5 px-3 cursor-pointer"
                    >
                      <Save className="w-3.5 h-3.5" />
                      Save Correction
                    </button>
                  )}
                </div>
              </div>

              {/* Requirement Value / Editor Card */}
              {!isEditing ? (
                <div className="bg-[#F7F6F1] p-4 rounded-lg border border-[#E5E2D9] space-y-1">
                  <span className="text-xs text-[#667085] block mb-1">Tender Specified Value:</span>
                  <p className="text-sm font-semibold text-[#17202A] font-mono">{selectedReq.specified_value}</p>
                  <div className="mt-2 flex items-center gap-2 text-xs">
                    <span className="text-[#667085]">Compliance Assessment:</span>
                    <span className="text-[#17202A] font-medium">{selectedReq.compliance_status}</span>
                  </div>
                </div>
              ) : (
                <div className="bg-white p-4 rounded-lg border border-[#087F73] space-y-3">
                  <span className="text-xs font-semibold text-[#087F73] block">Edit Requirement Parameter & Value:</span>
                  <div>
                    <label className="text-xs text-[#667085] block mb-1">Parameter Name:</label>
                    <input
                      type="text"
                      value={editParam}
                      onChange={(e) => setEditParam(e.target.value)}
                      className="w-full bg-[#F7F6F1] border border-[#D5D3C8] rounded p-2 text-xs text-[#17202A] font-mono focus:outline-none focus:border-[#087F73]"
                    />
                  </div>
                  <div>
                    <label className="text-xs text-[#667085] block mb-1">Specified Technical Value:</label>
                    <input
                      type="text"
                      value={editValue}
                      onChange={(e) => setEditValue(e.target.value)}
                      className="w-full bg-[#F7F6F1] border border-[#D5D3C8] rounded p-2 text-xs text-[#17202A] font-mono focus:outline-none focus:border-[#087F73]"
                    />
                  </div>
                </div>
              )}

              {/* Step-by-Step Justification Chain */}
              <div className="space-y-4 relative before:absolute before:left-4 before:top-3 before:bottom-3 before:w-0.5 before:bg-[#C0E3DF]">
                
                {/* Step 1: Standard Citation */}
                <div className="relative pl-10">
                  <div className="absolute left-2 top-0.5 -translate-x-1/2 p-1 rounded-full bg-[#087F73] text-white">
                    <FileText className="w-3.5 h-3.5" />
                  </div>
                  <div>
                    <span className="text-xs text-[#087F73] font-semibold uppercase">Step 1 — Standard Citation</span>
                    <h4 className="text-sm font-bold text-[#17202A] mt-0.5">{selectedReq.evidence_chain.standard_code}</h4>
                    <p className="text-xs text-[#667085]">{selectedReq.evidence_chain.standard_title}</p>
                  </div>
                </div>

                {/* Step 2: Clause & Page */}
                <div className="relative pl-10">
                  <div className="absolute left-2 top-0.5 -translate-x-1/2 p-1 rounded-full bg-[#2E6B5B] text-white">
                    <Info className="w-3.5 h-3.5" />
                  </div>
                  <div>
                    <span className="text-xs text-[#2E6B5B] font-semibold uppercase">Step 2 — Governing Clause</span>
                    <h4 className="text-sm font-medium text-[#17202A] mt-0.5">{selectedReq.evidence_chain.clause}</h4>
                    <span className="text-xs text-[#667085]">Page {selectedReq.evidence_chain.page_number} of BIS Document</span>
                  </div>
                </div>

                {/* Step 3: Exact Source Quote Evidence */}
                <div className="relative pl-10">
                  <div className="absolute left-2 top-0.5 -translate-x-1/2 p-1 rounded-full bg-[#A8752B] text-white">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                  </div>
                  <div>
                    <span className="text-xs text-[#A8752B] font-semibold uppercase">Step 3 — Source Evidence Quote</span>
                    <div className="mt-1.5 p-3.5 rounded-lg bg-[#FDF7ED] border border-[#F6E2C3] text-xs text-[#A8752B] font-mono italic leading-relaxed">
                      "{selectedReq.evidence_chain.quote}"
                    </div>
                  </div>
                </div>

              </div>

              {/* Warnings / Restrictiveness Notes */}
              {selectedReq.issue_description && (
                <div className="p-4 rounded-lg bg-[#FDF7ED] border border-[#F6E2C3] text-xs text-[#A8752B]">
                  <div className="flex items-center gap-2 font-semibold text-[#A8752B] mb-1">
                    <AlertTriangle className="w-4 h-4" />
                    <span>Issue / Restrictiveness Warning</span>
                  </div>
                  <p className="text-[#17202A]">{selectedReq.issue_description}</p>
                </div>
              )}

              {/* Source Provenance Footer */}
              <div className="pt-3 border-t border-[#E5E2D9] flex items-center justify-between text-xs text-[#667085]">
                <span>Source: {selectedReq.evidence_chain.provenance_source}</span>
                <button
                  type="button"
                  onClick={() => onSelectStandard && onSelectStandard(selectedReq.evidence_chain.standard_code)}
                  className="text-[#087F73] hover:text-[#066560] font-semibold inline-flex items-center gap-1 cursor-pointer"
                >
                  View Standard Record <ExternalLink className="w-3.5 h-3.5" />
                </button>
              </div>

            </div>
          )}
        </div>

      </div>
    </div>
  );
}
