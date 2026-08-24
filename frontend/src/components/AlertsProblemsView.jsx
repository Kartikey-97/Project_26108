import React, { useState } from 'react';
import { AlertTriangle, AlertCircle, History, ShieldAlert, CheckCircle2, UserCheck, Filter } from 'lucide-react';

export default function AlertsProblemsView({ requirements, standards, summary }) {
  const [filterType, setFilterType] = useState('ALL');

  const alertsList = [
    {
      id: 'alt-1',
      type: 'OUTDATED',
      title: 'Legacy Standard Referenced: IS 2149:1970',
      description: 'IS 2149:1970 has been withdrawn and superseded by IS 10322 (Part 5/Sec 3): 2012. Citation in procurement documents must be updated.',
      severity: 'HIGH',
      action: 'Replace IS 2149:1970 with IS 10322 (Part 5/Sec 3): 2012'
    },
    {
      id: 'alt-2',
      type: 'RESTRICTIVE',
      title: 'Proprietary / Overly Narrow Spec: CCT 5700K ± 50K',
      description: 'Tolerance of ± 50K is unnaturally narrow for LED chromaticity (standard allows ± 300K). High risk of vendor bias or single-supplier lock-in.',
      severity: 'HIGH',
      action: 'Relax tolerance to 5700K (Nominal) as per IS 16102 (Part 2)'
    },
    {
      id: 'alt-3',
      type: 'MISSING',
      title: 'Missing Standard Citation: IS 617 for Aluminum Housing',
      description: 'Housing material (ADC12 die-cast aluminum) is specified without citing IS 617 (Aluminum Casting Alloy standard).',
      severity: 'MEDIUM',
      action: 'Add reference to IS 617 Grade 4600'
    },
    {
      id: 'alt-4',
      type: 'HUMAN_REVIEW',
      title: 'Ambiguous Testing Location Requirement',
      description: 'Clause specifies "testing at NABL laboratory", but does not specify whether third-party type test report or routine test report is required.',
      severity: 'MEDIUM',
      action: 'Clarify whether Type Test Report from NABL accredited lab is required'
    }
  ];

  const filteredAlerts = filterType === 'ALL'
    ? alertsList
    : alertsList.filter(a => a.type === filterType);

  return (
    <div className="space-y-6 animate-fade-in">
      
      {/* Header Banner */}
      <div className="surface-card p-5 border-l-4 border-l-[#A84A42]">
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="badge badge-superseded">Audit & Alerts</span>
              <h2 className="text-base font-bold text-[#17202A]">Alerts, Conflicts & Quality Audit</h2>
            </div>
            <p className="text-xs text-[#667085]">
              Automated detection of outdated standards, missing references, restrictive specifications, and items requiring human review before tender publication.
            </p>
          </div>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="surface-card p-2 flex flex-wrap items-center gap-1.5 overflow-x-auto">
        <span className="text-xs text-[#667085] font-semibold px-2 flex items-center gap-1 shrink-0">
          <Filter className="w-3.5 h-3.5" /> Filter Alerts:
        </span>
        <button
          type="button"
          onClick={() => setFilterType('ALL')}
          className={`px-3 py-1 rounded text-xs font-semibold cursor-pointer transition-all ${
            filterType === 'ALL'
              ? 'bg-[#17202A] text-white'
              : 'bg-[#F7F6F1] text-[#667085] border border-[#E5E2D9] hover:text-[#17202A]'
          }`}
        >
          All Alerts ({alertsList.length})
        </button>
        <button
          type="button"
          onClick={() => setFilterType('OUTDATED')}
          className={`px-3 py-1 rounded text-xs font-semibold cursor-pointer transition-all ${
            filterType === 'OUTDATED'
              ? 'bg-[#A84A42] text-white'
              : 'bg-[#FBF1F0] text-[#A84A42] border border-[#F3D2CF] hover:bg-[#F3D2CF]'
          }`}
        >
          Outdated Standards (1)
        </button>
        <button
          type="button"
          onClick={() => setFilterType('RESTRICTIVE')}
          className={`px-3 py-1 rounded text-xs font-semibold cursor-pointer transition-all ${
            filterType === 'RESTRICTIVE'
              ? 'bg-[#A8752B] text-white'
              : 'bg-[#FDF7ED] text-[#A8752B] border border-[#F6E2C3] hover:bg-[#F6E2C3]'
          }`}
        >
          Vendor Bias Risks (1)
        </button>
        <button
          type="button"
          onClick={() => setFilterType('MISSING')}
          className={`px-3 py-1 rounded text-xs font-semibold cursor-pointer transition-all ${
            filterType === 'MISSING'
              ? 'bg-[#087F73] text-white'
              : 'bg-[#EDF6F5] text-[#087F73] border border-[#C0E3DF] hover:bg-[#C0E3DF]'
          }`}
        >
          Missing Specs (1)
        </button>
        <button
          type="button"
          onClick={() => setFilterType('HUMAN_REVIEW')}
          className={`px-3 py-1 rounded text-xs font-semibold cursor-pointer transition-all ${
            filterType === 'HUMAN_REVIEW'
              ? 'bg-[#17202A] text-white'
              : 'bg-[#F7F6F1] text-[#667085] border border-[#E5E2D9] hover:text-[#17202A]'
          }`}
        >
          Human Review Required (1)
        </button>
      </div>

      {/* Alerts Grid */}
      <div className="space-y-4">
        {filteredAlerts.map((alert) => (
          <div
            key={alert.id}
            className={`surface-card p-5 border-l-4 ${
              alert.severity === 'HIGH'
                ? 'border-l-[#A84A42]'
                : 'border-l-[#A8752B]'
            }`}
          >
            <div className="flex items-start gap-4">
              <div className={`p-3 rounded-lg border mt-0.5 shrink-0 ${
                alert.severity === 'HIGH'
                  ? 'bg-[#FBF1F0] border-[#F3D2CF] text-[#A84A42]'
                  : 'bg-[#FDF7ED] border-[#F6E2C3] text-[#A8752B]'
              }`}>
                {alert.type === 'OUTDATED' && <History className="w-6 h-6" />}
                {alert.type === 'RESTRICTIVE' && <AlertTriangle className="w-6 h-6" />}
                {alert.type === 'MISSING' && <AlertCircle className="w-6 h-6" />}
                {alert.type === 'HUMAN_REVIEW' && <UserCheck className="w-6 h-6" />}
              </div>

              <div className="flex-1 space-y-2">
                <div className="flex items-center justify-between">
                  <span className={`badge ${
                    alert.severity === 'HIGH' ? 'badge-superseded' : 'badge-amended'
                  }`}>
                    {alert.severity} SEVERITY — {alert.type.replace('_', ' ')}
                  </span>
                  <span className="text-xs text-[#9BA3AF]">Auto-Detected</span>
                </div>

                <h3 className="text-sm font-bold text-[#17202A]">{alert.title}</h3>
                <p className="text-xs text-[#667085]">{alert.description}</p>

                <div className="mt-3 p-3 rounded-lg bg-[#F7F6F1] border border-[#E5E2D9] flex items-center justify-between text-xs">
                  <span className="text-[#17202A] font-semibold flex items-center gap-1.5">
                    <CheckCircle2 className="w-4 h-4 text-[#2E6B5B]" />
                    Recommended Action: {alert.action}
                  </span>
                  <button
                    type="button"
                    className="btn-secondary text-[11px] py-1 px-2.5 cursor-pointer"
                  >
                    Apply Correction
                  </button>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

    </div>
  );
}
