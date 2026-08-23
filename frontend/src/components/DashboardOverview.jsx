import React from 'react';
import { Layers, ShieldAlert, BookOpen, AlertTriangle, CheckCircle, FileBadge } from 'lucide-react';

export default function DashboardOverview({ data }) {
  if (!data) return null;
  const { input_summary, restrictiveness_analysis } = data;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8 animate-fade-in">
      
      {/* Metric 1: Extracted Requirements */}
      <div className="surface-card p-5">
        <div className="flex items-center justify-between mb-3">
          <span className="text-xs font-semibold text-[#667085] uppercase tracking-wider">Specs Extracted</span>
          <div className="p-2 rounded-lg bg-[#EDF6F5] text-[#087F73] border border-[#C0E3DF]">
            <Layers className="w-5 h-5" />
          </div>
        </div>
        <div className="flex items-baseline gap-2">
          <span className="text-3xl font-bold text-[#17202A]">{input_summary.total_specs_extracted}</span>
          <span className="text-xs text-[#667085]">Structured Tech Specs</span>
        </div>
        <div className="mt-3 flex items-center gap-1.5 text-xs text-[#2E6B5B]">
          <CheckCircle className="w-3.5 h-3.5" />
          <span>100% Parsed & Mapped</span>
        </div>
      </div>

      {/* Metric 2: Mapped Indian Standards */}
      <div className="surface-card p-5">
        <div className="flex items-center justify-between mb-3">
          <span className="text-xs font-semibold text-[#667085] uppercase tracking-wider">BIS Standards</span>
          <div className="p-2 rounded-lg bg-[#EDF6F5] text-[#087F73] border border-[#C0E3DF]">
            <BookOpen className="w-5 h-5" />
          </div>
        </div>
        <div className="flex items-baseline gap-2">
          <span className="text-3xl font-bold text-[#17202A]">{input_summary.standards_count}</span>
          <span className="text-xs text-[#667085]">Applicable Standards</span>
        </div>
        <div className="mt-3 flex items-center gap-1.5 text-xs text-[#667085]">
          <span>IS 10322, IS 16102, IS 15885</span>
        </div>
      </div>

      {/* Metric 3: Quality Control Order (QCO) */}
      <div className="surface-card p-5">
        <div className="flex items-center justify-between mb-3">
          <span className="text-xs font-semibold text-[#667085] uppercase tracking-wider">Regulatory QCO</span>
          <div className="p-2 rounded-lg bg-[#EBF4F1] text-[#2E6B5B] border border-[#C4E2DA]">
            <FileBadge className="w-5 h-5" />
          </div>
        </div>
        <div className="flex items-baseline gap-2">
          <span className="text-2xl font-bold text-[#2E6B5B]">MANDATORY</span>
        </div>
        <div className="mt-3 flex items-center gap-1.5 text-xs text-[#2E6B5B]">
          <ShieldAlert className="w-3.5 h-3.5" />
          <span>BIS CRS Mark Required by Law</span>
        </div>
      </div>

      {/* Metric 4: Restrictiveness Risk Level */}
      <div className="surface-card p-5">
        <div className="flex items-center justify-between mb-3">
          <span className="text-xs font-semibold text-[#667085] uppercase tracking-wider">Vendor Bias Risk</span>
          <div className="p-2 rounded-lg bg-[#FDF7ED] text-[#A8752B] border border-[#F6E2C3]">
            <AlertTriangle className="w-5 h-5" />
          </div>
        </div>
        <div className="flex items-baseline gap-2">
          <span className="text-3xl font-bold text-[#A8752B]">{input_summary.overall_risk_score}</span>
          <span className="text-xs text-[#667085]">({restrictiveness_analysis.flagged_count} Flagged Spec)</span>
        </div>
        <div className="mt-3 flex items-center gap-1.5 text-xs text-[#A8752B]">
          <span>Narrow CCT Tolerance Window</span>
        </div>
      </div>

    </div>
  );
}
