import React, { useState } from 'react';
import { GitFork, History, ShieldAlert, FileText, ChevronDown, CheckCircle2, AlertCircle, ArrowUpRight } from 'lucide-react';

export default function StandardsIntelligenceView({ standards, onOpenModal }) {
  const [expandedId, setExpandedId] = useState(standards[0]?.id || null);

  const toggleExpand = (id) => {
    setExpandedId(expandedId === id ? null : id);
  };

  return (
    <div className="space-y-6 animate-fade-in">
      
      {/* Header Banner */}
      <div className="surface-card p-5 border-l-4 border-l-[#087F73]">
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="badge badge-qco">Innovation 3</span>
              <h2 className="text-base font-bold text-[#17202A]">Standard Relationship & Version Intelligence</h2>
            </div>
            <p className="text-xs text-[#667085]">
              Multi-dimensional mapping of Indian Standards (BIS): Active version tracking, amendments, normative dependencies, superseded standard alerts, and mandatory Quality Control Orders (QCOs).
            </p>
          </div>
        </div>
      </div>

      {/* Standards List & Graph Navigator */}
      <div className="space-y-4">
        {standards.map((std) => {
          const isExpanded = expandedId === std.id;
          const isSuperseded = std.status === 'SUPERSEDED';

          return (
            <div
              key={std.id}
              className={`surface-card border transition-all ${
                isSuperseded
                  ? 'border-l-4 border-l-[#A84A42]'
                  : 'hover:border-[#087F73]'
              }`}
            >
              
              {/* Card Header Row */}
              <div
                onClick={() => toggleExpand(std.id)}
                className="p-5 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 cursor-pointer select-none"
              >
                <div className="flex items-start gap-3">
                  <div className={`p-3 rounded-lg border mt-0.5 ${
                    isSuperseded
                      ? 'bg-[#FBF1F0] border-[#F3D2CF] text-[#A84A42]'
                      : 'bg-[#EDF6F5] border-[#C0E3DF] text-[#087F73]'
                  }`}>
                    <FileText className="w-6 h-6" />
                  </div>
                  <div>
                    <div className="flex flex-wrap items-center gap-2 mb-1">
                      <span className="text-base font-bold text-[#17202A] font-mono">{std.code}</span>
                      
                      {/* Status Badges */}
                      {std.status === 'CURRENT' && <span className="badge badge-current">CURRENT (2022)</span>}
                      {std.status === 'AMENDED' && <span className="badge badge-amended">AMENDED ({std.amendments.length})</span>}
                      {std.status === 'SUPERSEDED' && <span className="badge badge-superseded">SUPERSEDED / WITHDRAWN</span>}
                      {std.is_qco_mandatory && <span className="badge badge-qco">QCO MANDATORY</span>}
                    </div>
                    
                    <h3 className="text-sm font-semibold text-[#17202A]">{std.title}</h3>
                    <p className="text-xs text-[#667085] mt-1">Current Version: <span className="text-[#17202A] font-mono">{std.current_version}</span></p>
                  </div>
                </div>

                <div className="flex items-center gap-3 self-end md:self-auto">
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      onOpenModal(std);
                    }}
                    className="text-xs font-semibold text-[#087F73] hover:text-[#066560] bg-[#EDF6F5] px-3 py-1.5 rounded border border-[#C0E3DF] inline-flex items-center gap-1 cursor-pointer"
                  >
                    Inspect Clauses <ArrowUpRight className="w-3.5 h-3.5" />
                  </button>

                  <div className="p-1.5 rounded-lg bg-[#F7F6F1] border border-[#E5E2D9] text-[#667085]">
                    <ChevronDown className={`w-4 h-4 transition-transform ${isExpanded ? 'rotate-180' : ''}`} />
                  </div>
                </div>
              </div>

              {/* Expanded Intelligence Panel */}
              {isExpanded && (
                <div className="px-5 pb-5 pt-2 border-t border-[#E5E2D9] space-y-4 animate-fade-in">
                  
                  {/* Superseded Warning Banner */}
                  {isSuperseded && (
                    <div className="p-3.5 rounded-lg bg-[#FBF1F0] border border-[#F3D2CF] text-xs text-[#A84A42] flex items-start gap-2">
                      <AlertCircle className="w-4 h-4 text-[#A84A42] shrink-0 mt-0.5" />
                      <div>
                        <span className="font-semibold text-[#A84A42] block">Outdated Standard Warning</span>
                        <p className="text-[#17202A]">{std.withdrawal_reason}</p>
                      </div>
                    </div>
                  )}

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    
                    {/* Amendments Timeline */}
                    <div className="bg-[#FDF7ED] p-4 rounded-lg border border-[#F6E2C3] space-y-2">
                      <div className="flex items-center gap-2 text-xs font-semibold text-[#A8752B] uppercase tracking-wider">
                        <History className="w-4 h-4" />
                        <span>Amendments & Revision History</span>
                      </div>
                      {std.amendments && std.amendments.length > 0 ? (
                        <div className="space-y-2 mt-2">
                          {std.amendments.map((amd, idx) => (
                            <div key={idx} className="p-2.5 rounded-lg bg-white border border-[#F6E2C3] text-xs">
                              <div className="flex items-center justify-between text-[#A8752B] font-semibold mb-0.5">
                                <span>{amd.code}</span>
                                <span className="font-mono text-[#667085]">{amd.year}</span>
                              </div>
                              <p className="text-[#17202A]">{amd.description}</p>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <p className="text-xs text-[#9BA3AF] italic mt-1">No active amendments issued.</p>
                      )}
                    </div>

                    {/* Normative References & Cross Links */}
                    <div className="bg-[#EDF6F5] p-4 rounded-lg border border-[#C0E3DF] space-y-2">
                      <div className="flex items-center gap-2 text-xs font-semibold text-[#087F73] uppercase tracking-wider">
                        <GitFork className="w-4 h-4" />
                        <span>Normative / Allied References</span>
                      </div>
                      {std.normative_references && std.normative_references.length > 0 ? (
                        <div className="space-y-1.5 mt-2">
                          {std.normative_references.map((ref, idx) => (
                            <div key={idx} className="flex items-center gap-2 text-xs text-[#17202A] bg-white p-2 rounded border border-[#C0E3DF]">
                              <span className="w-1.5 h-1.5 rounded-full bg-[#087F73] shrink-0"></span>
                              <span>{ref}</span>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <p className="text-xs text-[#9BA3AF] italic mt-1">No normative references mapped.</p>
                      )}
                    </div>

                  </div>

                  {/* Regulatory QCO & CRS Card */}
                  {std.qco_details && (
                    <div className="p-4 rounded-lg bg-[#EDF6F5] border border-[#C0E3DF] text-xs flex flex-col md:flex-row items-start md:items-center justify-between gap-3">
                      <div className="flex items-start gap-2.5">
                        <ShieldAlert className="w-5 h-5 text-[#087F73] shrink-0 mt-0.5" />
                        <div>
                          <span className="font-bold text-[#17202A] text-sm block">{std.qco_details.order_name}</span>
                          <p className="text-[#667085] mt-0.5">
                            Issued by {std.qco_details.issuing_authority} (Effective {std.qco_details.effective_date})
                          </p>
                        </div>
                      </div>
                      <span className="badge badge-qco self-start md:self-auto">
                        BIS CRS Registration Mandatory
                      </span>
                    </div>
                  )}

                </div>
              )}

            </div>
          );
        })}
      </div>

    </div>
  );
}
